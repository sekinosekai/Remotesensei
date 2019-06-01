# InnovationProject
其实**表情分析**(Facial Expression Analysis)那一部分的实现相当玄学。如果按照玛丽女士的意思，用这个思路继续完成创新项目，问题不大；但是之后的毕设话就算了，毕竟我在答辩时真实的被examiner怼了qwq（她说我的算法用的太low）。

思路也挺简单粗暴的，在那天pre的时候解释的差不多了，就是：情绪分析（Microsoft Face API）+ 4种状态分类（返回的8个emotion intensity输入KNN classifier）+ gaze direction计算是否distracted（根据关键点计算）。具体内容就看report吧，report里面的语法错误啊用词不当啊那些……请尽情无视。

这里还有一部分代码是GUI的，一部分是控制机器人的。
