# Fiend
#### A Python module for accessing Zynga's [Words with Friends](https://market.android.com/details?id=com.zynga.words)

Author: Jahn Veach &lt;j@hnvea.ch&gt;  
License: GPLv3  
Website: https://github.com/v64/fiend  

### Purpose
Fiend gives you complete access to all the data related to your games, you and your opponents' moves, etc. Its primary purpose is to provide access to Words with Friends for users who can't use an already existing client. It's also designed for tracking statistics and other records in a way that no other client currently does.

Obviously, there are a number of ways this module could be used to facilitate cheating. That being said: I absolutely **DO NOT** condone the use of this module for any purpose that gives you an unfair advantage in Words with Friends.

### Caveat coder
This project is still young and not stable at all. None of the public methods or variables are set in stone, especially not anything starting with an underscore.

### Blog post by Scott Contini
[Scott Contini](https://littlemaninmyhead.wordpress.com/about/), a security researcher, wrote [a detailed blog post](https://littlemaninmyhead.wordpress.com/2016/04/09/words-with-friends-trusts-the-clients-a-little-too-much/) in 2016 examining the Words with Friends protocol. Fiend played a role in allowing him to interact with the Words with Friends server in an unrestricted way, demonstrating its usefulness as a debugging tool.

### Acknowledgements
I thank the authors of the following tools, which were invaluable in helping me write Fiend.

* dex2jar: http://code.google.com/p/dex2jar/
* JD-GUI: http://java.decompiler.free.fr/?q=jdgui 
* apktool: http://code.google.com/p/android-apktool/
* smali: http://code.google.com/p/smali/
* Shark for Root: https://market.android.com/details?id=lv.n3o.shark&feature=search\_result
* SQLite Database Browser: http://sqlitebrowser.sourceforge.net/
* unrevoked: http://unrevoked.com/

I also thank the Android development team for releasing a fine set of access and debugging tools for their platform.

Finally, thanks to Zynga for developing Words with Friends. Since Hasbro hasn't prevented you from making your own version of Scrabble, I hope you'll afford me a similar courtesy.
