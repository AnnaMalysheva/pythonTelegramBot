moveX = [-1, 0, 1, 0]
moveY = [0, -1, 0, 1]


def correct(i, j):
    if i < 0 or j < 0:
        return False
    if i >= n or j >= m:
        return False
    return True


def dfs(x, y):
    stack = []
    elem = [x, y]
    stack.append(elem)
    while len(stack) > 0:
        cur = stack.pop()
        for i in range(4):
            fx = cur[0] + moveX[i]
            fy = cur[1] + moveY[i]
            if correct(fx, fy) and A[fx][fy] == '#':
                A[fx][fy] = 'o'
                elem = [fx, fy]
                stack.append(elem)


n, m = map(int, input().split())
A = [[0] * m for i in range(n)]
for i in range(n):
    A[i] = list(input())

k = 0
for i in range(n):
    for j in range(m):
        if A[i][j] == '#':
            k = k + 1
            dfs(i, j)

print(k)
