
$git add "Stock_all_model.py"  123
$git commit -m "say any word"
$git log //显示历史版本
git config --global core.autocrlf false // 关闭换行符处理，换行符是Mac系统和window系统的换行符是不一样的，所以git会自动对提交代码的换行符进行转换，
# 在Git输入git log卡住解决方法:输入法切换英文,键入Q即可。出现原因:不明,有待后续探
输出信息中master 后是唯一的版本号，也是commitID通过该号码可以用git reset --hard commmitID 跳到对用的版本，输出信息如下
$ git commit -m " ka zhu "
[master 6a3bcf9]  ka zhu
1 file changed, 5 insertions(+), 7 deletions(-)

# 回退到上一个版本命令
git reset --hard HEAD^ 加两个^^ 就是回退上上次版本 Git的版本回退速度非常快，因为Git在内部有个指向当前版本的HEAD指针，当你回退版本的时候，Git仅仅是把HEAD从指向最后一个变成指向上一个：顺带更新了文件
┌────┐
│HEAD│
└────┘
   │
   └──> ○ append GPL
        │
        ○ add distributed
        │
        ○ wrote a readme file
改为指向add distributed：

┌────┐
│HEAD│
└────┘
   │
   │    ○ append GPL
   │    │
   └──> ○ add distributed
        │
        ○ wrote a readme file

后顺便把工作区的文件更新了。所以你让HEAD指向哪个版本号，你就把当前版本定位在哪。

现在，你回退到了某个版本，关掉了电脑，第二天早上就后悔了，想恢复到新版本怎么办？找不到新版本的commit id怎么办？

在Git中，总是有后悔药可以吃的。当你用$ git reset --hard HEAD^回退到add distributed版本时，再想恢复到append GPL，就必须找到append GPL的commit id。Git提供了一个命令git reflog用来记录你的每一次命令

终于舒了口气，从输出可知，append GPL的commit id是1094adb，现在，你又可以乘坐时光机回到未来了。

现在总结一下：

HEAD指向的版本就是当前版本，因此，Git允许我们在版本的历史之间穿梭，使用命令git reset --hard commit_id。

穿梭前，用git log可以查看提交历史，以便确定要回退到哪个版本。

要重返未来，用git reflog查看命令历史，以便确定要回到未来的哪个版本。

所以，git add命令实际上就是把要提交的所有修改放到暂存区（Stage），然后，执行git commit就可以一次性把暂存区的所有修改提交到分支。



