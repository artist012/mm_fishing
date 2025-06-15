import cv2
import numpy as np
from mss import mss
from pynput import keyboard, mouse
import time

class Hook:
    def __init__(self, threshold=0.3):
        """
        낚시 ㄱㄱ
        
        Args:
            threshold (float): 매칭 임계값 (0.0 ~ 1.0)
        """
        
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()

        self.threshold = threshold

        self.sct = mss()
        self.monitor = self.sct.monitors[0]

    def test(self):
        screen_img = self.capture_screen()
        found, match = self.find_image('hook_fish')
        
        result_img = screen_img.copy()
        
        if found:
            print(f"매칭을 찾았습니다:")
            # 사각형 그리기
            cv2.rectangle(result_img, 
                match['top_left'],
                match['bottom_right'],
                (0, 255, 0), 2)
            
            # 중심점 표시
            cv2.circle(result_img, match['center'], 5, (0, 0, 255), -1)
            
            # 신뢰도 텍스트 표시
            confidence_text = f"{match['confidence']:.2f}"
            cv2.putText(result_img, confidence_text,
                (match['top_left'][0], match['top_left'][1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            print(f"  매칭 {1}: 위치 {match['center']}, 신뢰도: {match['confidence']:.3f}")
        else:
            print("이미지를 찾을 수 없습니다.")

    # 낚시 버튼 찾기
    def start_hook(self):
        while True:
            found, match = self.find_image('hook')
            
            if found:
                self.mouse.position = (match['center'][0] + self.monitor['left'], match['center'][1] + self.monitor['top'])
                self.mouse.click(mouse.Button.left)
                break
            else:
                self.keyboard.press('w')
                self.keyboard.release('w')
                continue

    # 물고기 기다리기
    def wait_fish(self):
        while True:
            found, match = self.find_image('hook_fish')

            if found:
                return match['center']

    # 물고기 입질옴
    #
    # 반응이 왔다.,
    # 뭔가 걸렸다,
    # 라는 멘트는 잡템
    def hooking_fish(self):
        found, match = self.find_image('hook_fish')

        if found:
            self.mouse.position = (match['center'][0] + self.monitor['left'], match['center'][1] + self.monitor['top'])
            self.mouse.click(mouse.Button.left)
            return True
        else:
            return False

    def check_waste(self):
        screen_img = self.capture_screen()
        
        waste1, _ = self.find_image('waste1', screen_img)
        waste2, _ = self.find_image('waste2', screen_img)

        if waste1 or waste2:
            return True
        else:
            return False

    # 낚시중인지 체크
    def is_fishing(self):
        found, _ = self.find_image('is_fishing')
        return found

    def capture_screen(self):
        """화면을 캡처하여 OpenCV 이미지로 반환"""
        screenshot = self.sct.grab(self.monitor)
        # mss는 BGRA 형식으로 반환하므로 BGR로 변환
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    
    def find_image(self, name, screen_img=None):
        """
        화면에서 템플릿 이미지를 찾기

        Args:
            name: 찾을 이미지 이름
            screen_img: 화면 이미지 (없어도 됨)

        Returns:
            tuple: (found, match) - found는 boolean, match는 가장 신뢰도 높은 매치의 위치
        """

        if screen_img is None:
            screen_img = self.capture_screen()

        template = cv2.imread(f'image/{name}.png', cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"템플릿 이미지를 로드할 수 없습니다: {name}")

        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)

        # 가장 높은 신뢰도의 위치 찾기
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= self.threshold:
            h, w = template.shape[:2]
            match = {
                'top_left': max_loc,
                'bottom_right': (max_loc[0] + w, max_loc[1] + h),
                'center': (max_loc[0] + w//2, max_loc[1] + h//2),
                'confidence': max_val
            }
            return True, match
        else:
            return False, None