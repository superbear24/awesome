"""
1.元组与列表类似，但是里面的元素不能修改
2.元组使用(), 列表使用[]
"""
def p(arg):
    print(arg)


tup = ()
tup1 = (199,)   # 当元组只包含一个元素时，需要在元素后面加逗号
p(tup1[0])      # 获取元组中的值

max(list1)              # 元组 最大值
min(lis1)               # 元组 最小值
len(list1)              # 元组长度