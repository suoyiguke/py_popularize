for j in range(5):
    for k in range(5):
        if j == k == 3:
            print('程序即将break跳出一层')
            break
        else:
            print(j, '----', k)
    else:  # else1
        continue
    print('程序即将break跳出二层')
    break  # break1
