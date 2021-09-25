n, m = map(int, input().split())
W = [set() for i in range(n + 1)]
for i in range(m):
    u, v = map(int, input().split())
    W[u].add(v)
# W[v].add(u)

Color = [0] * (m + 1)
CycleFound = False


def DFS(start):
    global CycleFound
    Color[start] = 1
    for u in W[start]:
        if Color[u] == 0:
            DFS(u)
        elif Color[start] == 1:
            CycleFound = True
            break
        Color[start] = 2
    if CycleFound:
        return

for i in range(1, m + 1):
    if Color[i] == 0:
        DFS(i)
    if CycleFound:
        break

if CycleFound:
    print("No")
else:
    print("Yes")