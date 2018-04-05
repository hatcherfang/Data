## ZooKeeper Fuction  
1. 提供一个小型的数据节点, 这些节点被称为znode, 采用类似于文件系统的层级树状结构进行管理。  
2. 数据节点会在整个zookeeper集群中同步, 用户在编写分布式应用时,可以在zookeeper集群中存储一些公用  
信息在里面。   
3. 编写的分布式应用也可以通过创建一个临时节点的方式, 实现互斥锁的功能。  
4. ZooKeeper可以实现主从模式, 首先一个客户端创建一个/master临时节点, 当别的客户端再创建/master临时节点  
的时候就会报错,这时候创建/master节点的会话就作为master,而别的客户端就作为worker, 同时别的客户端对/master节点  
设置监视点, 当作为master的会话删除了master节点或者master会话断开, 这时候其它worker就会得到消息, 并重新选举  
创建master节点, 产生新的master节点。  
5. client在接收一个znode变更通知并设置新的监视点时, znode节点也许发生了新的变化, 但是不会错过这些变化,   
原因是client端在设置监视点前读取ZooKeeper的状态, 最终client不会错过任何变更。  
6. 脑裂(split-brain): 系统中两个或者多个部分开始独立工作, 导致整体行为不一致。  
7. 集群节点总数最好是奇数个, 容忍服务器崩溃的个数不超过1/3。防止服务器之间发生长时间分区隔离, 数据不一致产生脑裂现象。    
## ZooKeeper架构   
1. ZooKeeper服务器端运行于两种模式下: 独立模式(standalone) 和仲裁模式(quorum)。  
独立模式几乎与其术语所描述的一样: 有一个单独的服务器, ZooKeeper状态无法复制。  
仲裁模式指具有一组ZooKeeper服务器, 我们称为ZooKeeper集合(ZooKeeper ensemble),它们之前可以  
进行状态的复制, 并同时为服务于客户端的请求。  
