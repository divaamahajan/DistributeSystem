import time
def fn2():
    n = 0
    while True:
        n += 1
        time.sleep(1)
        try:
            print("in while try")
            x = fn1(n)
            print(f"hello {x}")
        except Exception as e:
            print("in while exception")
            break
    print("OUT While loop")



def fn1(n):
    try:
        print("fn1 try")
        raise Exception()
    except Exception as e:
        print("fn1 exception")
        fn3()
        # raise Exception("")
    return n

def fn3():
    raise Exception
fn2()