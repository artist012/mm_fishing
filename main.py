from time import sleep
from hook import Hook

def main():
    sleep(3)

    hook = Hook(threshold=0.8)
    print('세팅 완료\n')

    while True:
        hook.start_hook()
        print('낚시를 시작합니다')
        sleep(1)
        if hook.is_fishing():
            print('물고기 기다리기 시작')
            hook.wait_fish()
            print('입질이 왔습니다')

            is_waste = hook.check_waste()
            if is_waste:
                print('쓰레기가 낚였습니다\n재시작 합니다\n')
                continue

            sleep(5)

            res = hook.hooking_fish()
            if res:
                print('물고기를 낚았습니다\n재시작 합니다\n')
            else:
                print('물고기를 낚는데 실패했습니다\n재시작 합니다\n')                
        else:
            print("의도치 않게 낚시가 종료되었습니다\n재시작 합니다.\n")
            continue

if __name__ == "__main__":
    main()