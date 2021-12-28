
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

第一次修改 -> git add -> 第二次修改 -> git commit

你看，我们前面讲了，Git管理的是修改，当你用git add命令后，在工作区的第一次修改被放入暂存区，准备提交，但是，在工作区的第二次修改并没有放入暂存区，所以，git commit只负责把暂存区的修改提交了，也就是第一次的修改被提交了，第二次的修改不会被提交。

提交后，用git diff HEAD -- readme.txt命令可以查看工作区和版本库里面最新版本的区别：

Git同样告诉我们，用命令git reset HEAD <file>可以把暂存区的修改撤销掉（unstage），重新放回工作区

git reset命令既可以回退版本，也可以把暂存区的修改回退到工作区。当我们用HEAD时，表示最新的版本。

指定git status 显示
Changes to be committed: # 暂存区有数据但是没有执行git commit -m
  (use "git restore --staged <file>..." to unstage)
        modified:   readme.txt

Changes not staged for commit: # 工作区有修改还未提交到暂存区的
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   readme.txt

Untracked files: # 没有纳入到git的文件
  (use "git add <file>..." to include in what will be committed)
        ../../../dnm
还记得如何丢弃工作区的修改吗？

$ git checkout -- readme.txt


又到了小结时间。

场景1：当你改乱了工作区某个文件的内容，想直接丢弃工作区的修改时，用命令git checkout -- file。

场景2：当你不但改乱了工作区某个文件的内容，还添加到了暂存区时，想丢弃修改，分两步，第一步用命令git reset HEAD <file>，就回到了场景1，第二步按场景1操作。

场景3：已经提交了不合适的修改到版本库时，想要撤销本次提交，参考版本回退一节，不过前提是没有推送到远程库。

现在，我们根据GitHub的提示，在本地的learngit仓库下运行命令：

$ git remote add origin git@github.com:michaelliao/learngit.git
git remote add origin git@github.com:XiaoRuMiLi/GitStore.git

请千万注意，把上面的michaelliao替换成你自己的GitHub账户名，learngit换成你的远程仓库名.否则，你在本地关联的就是我的远程库，关联没有问题，但是你以后推送是推不上去的，因为你的SSH Key公钥不在我的账户列表中。

添加后，远程库的名字就是origin，这是Git默认的叫法，也可以改成别的，但是origin这个名字一看就知道是远程库。

把本地库的内容推送到远程，用git push命令，实际上是把当前分支master推送到远程。

由于远程库是空的，我们第一次推送master分支时，加上了-u参数，Git不但会把本地的master分支内容推送的远程新的master分支，还会把本地的master分支和远程的master分支关联起来，在以后的推送或者拉取时就可以简化命令。
git remote add origin git@github.com:xiaoRuMiLi/GitStore.git

需要在gethub网站设置ssl 秘钥， 秘钥在本地仓库根目录打开Git bash Here 获取 参考该内容，廖雪峰忽略了该内容，导致跟着他的方法不能上传到远程库，需要特别注意参看内容如下
https://blog.csdn.net/weixin_44394753/article/details/91410463

现在，远程库已经准备好了，下一步是用命令git clone克隆一个本地库：

$ git clone git@github.com:xiaoRuMiLi/jinjie.git
Cloning into 'gitskills'...

不同的机器连接到同一个远程仓库都必须要把本地的ssh key 复制到GitHub网站，才能正常clone远程到本地，正常push到远程，本地没有成成国sshkey 的可以用命令生成，已经生成的可以用命令查看,具体操作流程详见https://git-scm.com/book/zh/v2/%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8A%E7%9A%84-Git-%E7%94%9F%E6%88%90-SSH-%E5%85%AC%E9%92%A5

error: Your local changes to the following files would be overwritten by merge 解决方案

团队其他成员修改了某文件并已提交入库，你在pull之前修改了本地该文件，等你修改完代码再pull时，这时会报错如下错误：

error: Your local changes to the following files would be overwritten by merge

二、解决方案
根据是否要保存本地修改，有以下两种解决方案

2.1  保留修改
执行以下三条命令

git stash #封存修改
git pull origin master
git stash pop #把修改还原


所以，对很多开发人员而言，一打开电脑，马上先git pull，拉取最新的。然后进行常规开发，
开发完毕之后，在git push之前，还需要使用git pull再拉取一遍。
如果还有一个新的程序员丙，加入了，怎么办呢？

相应的，每个程序员都可以拥有自己的分支，可以进行任何的开发，此时和master没有什么关系的。

一旦开发完毕，就可以将你的分支合并到主分支上去。

什么时候会用到分支呢？

假设你准备开发一个新功能，但是需要两周才能完成，第一周你写了50%的代码，如果立刻提交，由于代码还没写完，不完整的代码库会导致别人不能干活了。如果等代码全部写完再一次提交，又存在丢失每天进度的巨大风险，怎么办？

你可以创建一个属于自己的分支，别人看不见，还继续在原来的分支上工作，而你在自己的分支上进行开发，等开发完毕，合并即可。

在开源世界中，需用大量的程序员共同维护一个项目。也是需要使用分支，如Jquery。
多人开发策略可以参考这个文章https://blog.csdn.net/wangliang888888/article/details/80536277


一次提交多个文件的方法
    cd 到需要提交的文件夹中，执行git add .  注意是add空格加点符号。 这个是提交所有文件到暂存区，
    git commit -m 提交修改
    git push -u origin master 推送到远程仓库，有可能需要你输入账号和密码


1.git log退出方法
    使用git log之后无法回到主页面,最后只能暴力关闭git bash. 解决方法其实很简单,输入字母Q即可退出.