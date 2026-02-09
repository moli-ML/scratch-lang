: 开始

@ 舞台
变量: score = 39
变量: aoto play = 4
变量: 上一次的分数 = 39
变量: 预测 = -156.61515560435572
变量: 1 = -18.109048512937804
变量: 2 = -186.08374372340216
变量: x = 1835.3272176174528
变量: y = 129.22870475298413
变量: min = 129.22870475298413
变量: 4 = -148.75149417955038
变量: sum = -5676.838993042221
变量: 平均 = -145.55997418056975
变量: 3 = 0
变量: 5 = -150.09157502838383
列表: 1
// 造型: background
// 音效: 啵


# paddle
// 造型: paddle

当绿旗被点击

将y坐标设为 -160
设置 ~aoto play 为 "4"
广播 ?
重复执行
  将x坐标设为 ?
  结束

当收到 0
重复执行
  将x坐标设为 鼠标的x坐标
  结束

当收到 1
重复执行
  将x坐标设为 ball 的 x position
  结束

当收到 2
重复执行
  如果 (ball 的 y position < "-140") 那么
    将x坐标设为 ball 的 x position
    结束
  结束

当收到 3
重复执行
  如果 (ball 的 y position < "-120") 那么
    将x坐标设为 ball 的 x position
    结束
  结束

当收到 4
广播 "消息1"
重复执行
  将x坐标设为 ?
  结束

重复执行
  如果 ((不是 (? = ?)) 或 (? = "0")) 那么
    等待 ? 秒
    结束
  广播 "消息1" 并等待
  结束

当收到 5
广播 "消息2"
重复执行
  将x坐标设为 ?
  结束

当绿旗被点击
将y坐标设为 -160
设置 ~aoto play 为 "4"
广播 ?
重复执行
  将x坐标设为 ?
  结束


# ball
// 造型: ball-soccer
// 音效: pop

当绿旗被点击
删除 1 的全部项目
设置 ~sum 为 "0"
移到 0 50
面向 在 135 到 225 间取随机数 方向
设置 ~score 为 "0"
重复执行
  移动 10 步
  碰到边缘就反弹
  克隆 自己
  如果 碰到 [sensing_touchingobjectmenu] 那么
    设置 ~4 为 y坐标
    将 ? 加入 1
    将 ~sum 增加 ?
    将 ~score 增加 1
    设置 ~5 为 x坐标
    播放声音 pop
    面向 (180 - 方向) 方向
    旋转右 在 -10 到 10 间取随机数 度
    重复执行直到 (不是 碰到 [sensing_touchingobjectmenu])
    结束
  如果 碰到 [sensing_touchingobjectmenu] 那么
    停止 all
    结束
  设置 ~平均 为 (? / ?)
  结束

当作为克隆体启动时
重复 ? 次
  将 ghost 特效增加 10
  结束
删除此克隆体


# deathLine
// 造型: 造型1
// 音效: 啵

当绿旗被点击
移到 0 0


# ball2
// 造型: ball-soccer
// 音效: pop
// 自定义积木定义: 最多几步

当收到 消息1
重复执行
  将 ~3 增加 0
  最多几步
  移动 (ceiling (? / 10) * 10) 步
  如果 (? = "1") 那么
    克隆 自己
    结束
  碰到边缘就反弹
  如果 (不是 (y坐标 > "-145")) 那么
    设置 ~预测 为 x坐标
    设置 ~3 为 "0"
    面向 ball 的 direction 方向
    移到 ball 的 x position ball 的 y position
    结束
  结束

当绿旗被点击
设置 ~3 为 "0"
设置 ~上一次的分数 为 "0"
面向 ball 的 direction 方向
移到 ball 的 x position ball 的 y position
重复执行
  如果 (不是 (? = ?)) 那么
    设置 ~上一次的分数 为 ?
    设置 ~3 为 "0"
    面向 ball 的 direction 方向
    移到 ball 的 x position ball 的 y position
    结束
  结束

等待 ? 秒

如果 ((不是 (? = ?)) 或 (? = "0")) 那么
  设置 ~上一次的分数 为 ?
  面向 ball 的 direction 方向
  移到 ball 的 x position ball 的 y position
  重复执行
    移动 100 步
    碰到边缘就反弹
    如果 碰到 [sensing_touchingobjectmenu] 那么
      面向 ball 的 direction 方向
      移到 ball 的 x position ball 的 y position
      如果 (不是 (y坐标 > "-150")) 那么
        设置 ~预测 为 x坐标
        停止 this script
        结束
      否则
      如果 (不是 (y坐标 > "-150")) 那么
        设置 ~预测 为 x坐标
        停止 this script
        结束
      结束
    结束
  结束

如果 ((不是 (? = ?)) 或 (? = "0")) 那么
  设置 ~上一次的分数 为 ?
  面向 ball 的 direction 方向
  移到 ball 的 x position ball 的 y position
  结束

设置 ~预测 为 x坐标

如果 碰到 [sensing_touchingobjectmenu] 那么
  停止 this script
  结束

如果 (四舍五入 y坐标 = "-160") 那么
  结束

面向 ball 的 direction 方向
移到 ball 的 x position ball 的 y position

// 扩展积木 [procedures]: definition [procedures_prototype]
设置 ~1 为 y坐标
设置 ~2 为 x坐标
移动 1 步
设置 ~x 为 "0"
设置 ~y 为 "0"
如果 ("90" > abs 方向) 那么
  设置 ~y 为 ((168 - y坐标) / (y坐标 - ?))
  结束
如果 ("90" < abs 方向) 那么
  设置 ~y 为 ((-145 - y坐标) / (y坐标 - ?))
  结束
如果 ("0" > 方向) 那么
  设置 ~x 为 ((-227 - x坐标) / (x坐标 - ?))
  结束
如果 ("0" < 方向) 那么
  设置 ~x 为 ((227 - x坐标) / (x坐标 - ?))
  结束
如果 (? > ?) 那么
  设置 ~min 为 ?
  否则
  设置 ~min 为 ?
  结束

移动 -1 步

移动 ? 步

如果 (不是 (y坐标 > "-160")) 那么
  结束

重复执行直到 (((abs 方向 - 180) < "0") 或 ((abs 方向 - 180) > "2"))

当作为克隆体启动时
显示
等待 ? 秒
删除此克隆体

当绿旗被点击

重复执行
  碰到边缘就反弹
  结束

面向 ball 的 direction 方向
移到 ball 的 x position ball 的 y position


# ball3
// 造型: ball-soccer
// 音效: pop

如果 碰到 [sensing_touchingobjectmenu] 那么
  将 ~score 增加 1
  播放声音 pop
  面向 (180 - 方向) 方向
  旋转右 在 -10 到 10 间取随机数 度
  结束
如果 碰到 [sensing_touchingobjectmenu] 那么
  停止 all
  结束

当收到 消息2
重复执行
  移动 20 步
  碰到边缘就反弹
  如果 (不是 (y坐标 > "-145")) 那么
    设置 ~预测 为 x坐标
    面向 ball 的 direction 方向
    移到 ball 的 x position ball 的 y position
    结束
  结束

当绿旗被点击
移到 ball
面向 ball 的 direction 方向

