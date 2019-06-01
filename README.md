# InnovationProject
其实**表情分析**(Facial Expression Analysis)那一部分的实现相当玄学。如果按照玛丽女士的意思，用这个思路继续完成创新项目，问题不大；但是之后的毕设话就算了，毕竟我在答辩时真实的被examiner怼了qwq（她说我的算法用的太low，如果要提升的话我觉得还不如直接通过图像分类那四种状态，或许可以考虑openpose？就是需要很大的数据集，比较好的cpu或者gpu……）。

思路也挺简单粗暴的，在那天pre的时候解释的差不多了，就是：情绪分析（Microsoft Face API）+ 4种状态分类（返回的8个emotion intensity输入KNN classifier）+ gaze direction计算是否distracted（根据关键点计算）。具体内容就看report吧，report里面的语法错误啊用词不当啊那些……请尽情无视。

`classifierKNN.py: 使用了knn算法的分类器，数据集是那四个csv文件（包含8个emotion intensity）
recognition.py: 分析面部表情的函数，调用classifierKNN.py
pub.py: 通过socket给sub.py发送状态号码（0 to 3），同时显示图表
control.py: 包含控制机器人的函数。b1-b15.txt是每个动作的参数；包含script字样的是控制机器人说话的内容。
sub.py: 调用control.py，控制机器人`

ps:还有一部分GUI的代码（这部分代码主要是用来答辩时候演示表情识别的，没有包含所谓的tracking face的代码，实际上我觉得这个tracking确实很鸡肋……）
pps:代码里面一些保存路径需要改改
