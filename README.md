# Python-socket-programming
This is a Python network Programming project as a FTP Server              

本FTP服务器支持以下命令：
ls    listdir, 作用：列出当前目录的文件                                        
cd +  跳转目录                                            
put + 本机文件(本机使用绝对路径)       作用：上传文件到FTP服务器                           
get + 文件名    (默认下载位置为打开脚本的位置，类似于wget)    作用：从FTP服务器上下载文件                                          

当前版本的主动模式会有BUG，还在修复中

完成版会支持用户登录认证，使用JSON文件作为配置文件                       
