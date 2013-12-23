2014年值得你阅读的100本书
========================

# 前言 #

2013年就要结束了，2014年又如何呢？在[第一财经周刊](http://www.cbnweek.com/)的网站上看到了这个专题——[值得你阅读的100本书-2014年开始摆脱庸常生活](http://www.cbnweek.com/v/subject?id=22)。感觉还不错，制作这个小册子也是自己2014年读书的一个清单。

此外想要试一下[如何使用Markdown写书](https://github.com/larrycai/kaiyuanbook/blob/master/zh/chapters/01-chapter3.markdown)，之前已经试过了如何[使用Sphinx和reStructuredText作为写出工具](http://myshare.dscloud.me/scipydoc/pydoc_write_tools.html)，并整理完成了一个笔记——[工程设计方法学](http://conanxincv.sinaapp.com/project1/index.html)，放在了SAE上。不过使用reStructuredText时，多少还是有些不习惯。所以这里就使用Markdown来完成这本小册子。

## 说明 ##

1. 源码放在了[Github](https://github.com/conanxin/2014books)上：
    
		git clone https://github.com/conanxin/2014books.git

2. 下面介绍在Ubuntu上编译，先安装软件：
	
	    $ sudo apt-get install ruby1.9.1
    	$ sudo apt-get install pandoc
    	$ sudo apt-get install texlive-xetex
    	$ sudo apt-get install texlive-latex-recommended # main packages
    	$ sudo apt-get install texlive-latex-extra # package titlesec
	
	安装中文字体：
	
		$ sudo apt-get install ttf-arphic-gbsn00lp ttf-arphic-ukai # from arphic 
		$ sudo apt-get install ttf-wqy-microhei ttf-wqy-zenhei # from WenQuanYi

3. 使用命令：

		$ bash ./mmd2bok

### 注意 ###

现在生成的pdf格式并不是很perfect，因为我修改了文件**mmd2bok**中的内容。原因是我在Ubuntu上安装**[multimarkdown](http://fletcherpenney.net/multimarkdown/)**没有成功，不知道什么地方出了问题。 

然后我将下面的代码：

		multimarkdown -t latex meta.txt ../contents/0-preface*.markdown -o preface.tex
		multimarkdown -t latex meta.txt ../contents/1-chapter*.markdown -o chapters.tex
		multimarkdown -t latex meta.txt ../contents/2-appendix*.markdown -o appendix.tex

改成了：

		pandoc -t latex ../contents/0-preface*.markdown -o preface.tex
		pandoc -t latex ../contents/1-chapter*.markdown -o chapters.tex
		pandoc -t latex ../contents/2-appendix*.markdown -o appendix.tex

