# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-09-16 22:07:58
# @Last Modified by:   Marte
# @Last Modified time: 2021-09-28 21:08:52
#
# #我们有时会使出一招“全部导入”，也就是这样：
# from lib import *
#这时 import 就会把注册在包__init__.py 文件中 __all__ 列表中的子模块和子包导入到当前作用域中来。比如
__all__= ['MYSQL','CAPITAL','TUSHARE']