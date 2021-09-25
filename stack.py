n, q = map(int, input().split())
st_who = []
st_what = []
result = []
for i in range(q):
    a = list(map(int, input().split()))
    if a[0] == 1:
        if a[1] in st_who:
            index = st_who.index(a[1])
            st_who[index] = 0
        st_what.append(a[2])
        st_who.append(a[1])
    if a[0] == 2:
        if a[1] in st_what:
            index = st_what.index(a[1])
            found = st_who[index]
            if found == 0:
                result.append(a[1])
            else:
                while found in st_what:
                    index = st_what.index(found)
                    found = st_who[index]
                if found == 0:
                    result.append(a[1])
                else:
                    result.append(found)
        else:
            result.append(a[1])

print(*result)