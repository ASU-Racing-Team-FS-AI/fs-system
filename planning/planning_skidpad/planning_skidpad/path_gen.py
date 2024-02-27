import rclpy
from rclpy.node import Node
import math
import matplotlib.pyplot as plt
from sympy import *
import numpy as np
import pandas as pd

from geometry_msgs.msg import PoseArray
from nav_msgs.msg import Odometry
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

class SendPath(Node):

    def __init__(self):
        super().__init__('ConesPublisher')
        self.pathPub = self.create_publisher(Path, '/path', 10)
        self.subscription = self.create_subscription(PoseArray,'cones',self.listener_callback,10)
        self.subscription_state = self.create_subscription(Odometry, 'state', self.stateCallback,10)
        self.subscriptions
        self.finalPath = Path()
        self.state=Odometry()
        self.pastPos=[0,0]
        self.conePositions=np.array([])
        self.count = 0
        self.origin = [0,0]
        self.i=0
    
    def stateCallback(self, state:Odometry):
        
        if self.state != None:
            self.pastPos = [self.state.pose.pose.position.x,self.state.pose.pose.position.y]
        self.state = state
        self.get_logger().info(f'New state')

    def listener_callback(self, msg:PoseArray):
        #self.get_logger().info(f'New map')
        conesPosition= PoseArray()
        conesPosition= msg.poses
        self.conePositions = np.array([])
        self.conePositions = np.array([[i.position.x, i.position.y, i.position.z] for i in conesPosition])
        path=[]
        self.finalPath.poses=[]
        path=self.getPath()

        for i in path:
            pose = PoseStamped()
            pose.pose.position.x = float(i[0])
            pose.pose.position.y = float(i[1])
            self.finalPath.poses.append(pose)
        self.finalPath.header.frame_id = "map"
        #self.pathOrangeNodes.header.stamp = self.get_clock().now().to_msg()
        self.pathPub.publish(self.finalPath)
        #print(self.state.pose.pose.position.x,self.state.pose.pose.position.y)
        
    def conesClassification(self):

        rightBlueCones = np.array(self.conePositions[self.conePositions[:, 2] == 3][self.conePositions[self.conePositions[:, 2] == 3][:, 0] > 0])
        leftBlueCones = np.array(self.conePositions[self.conePositions[:, 2] == 3][self.conePositions[self.conePositions[:, 2] == 3][:, 0] <= 0])
        rightYellowCones = np.array(self.conePositions[self.conePositions[:, 2] == 4][self.conePositions[self.conePositions[:, 2] == 4][:, 0] > 0])
        leftYellowCones = np.array(self.conePositions[self.conePositions[:, 2] == 4][self.conePositions[self.conePositions[:, 2] == 4][:, 0] <= 0])
        orangeCones = np.array(self.conePositions[self.conePositions[:, 2] == 1])
        bigOrange = np.array(self.conePositions[self.conePositions[:, 2] == 2])

        rightBlueCones = rightBlueCones[np.argsort((rightBlueCones[:, 0] - self.state.pose.pose.position.x)**2 + (rightBlueCones[:, 1] - self.state.pose.pose.position.y)**2)]
        leftBlueCones = leftBlueCones[np.argsort((leftBlueCones[:, 0] - self.state.pose.pose.position.x)**2 + (leftBlueCones[:, 1] - self.state.pose.pose.position.y)**2)]
        rightYellowCones = rightYellowCones[np.argsort((rightYellowCones[:, 0] - self.state.pose.pose.position.x)**2 + (rightYellowCones[:, 1] - self.state.pose.pose.position.y)**2)]
        leftYellowCones = leftYellowCones[np.argsort((leftYellowCones[:, 0] - self.state.pose.pose.position.x)**2 + (leftYellowCones[:, 1] - self.state.pose.pose.position.y)**2)]
        orangeCones = orangeCones[np.argsort((orangeCones[:, 0] - self.state.pose.pose.position.x)**2 + (orangeCones[:, 1] - self.state.pose.pose.position.y)**2)]
        bigOrange = bigOrange[np.argsort((bigOrange[:, 0] - self.state.pose.pose.position.x)**2 + (bigOrange[:, 1] - self.state.pose.pose.position.y)**2)]

        return rightBlueCones.tolist(), leftBlueCones.tolist(), rightYellowCones.tolist(), leftYellowCones.tolist(), orangeCones.tolist(), bigOrange.tolist()

    def OrangeNodes(self,map: list)->list:
        OrangeNodes = []
        for i in map:
            lowestDist = float('inf')
            nearestNode = []
            for j in map:
                if i != j:
                    dist=math.sqrt((i[0]-j[0])**2+(i[1]-j[1])**2)
                    if (i[2]==1 and j[2]==1 and i[1] == j[1]) or (i[2]==3 and j[2]==4) or (i[2]==4 and j[2]==3) or (i[2]==2 and j[2]==2):
                        if dist < lowestDist:
                            lowestDist = dist
                            nearestNode = j
            if nearestNode != []:        
                #plt.plot([i[0],nearestNode[0]],[i[1],nearestNode[1]],'r-')
                if [round((i[0]+nearestNode[0])/2,2),round((i[1]+nearestNode[1])/2,2),1] not in OrangeNodes and[round((i[0]+nearestNode[0])/2,2),round((i[1]+nearestNode[1])/2,2),2] not in OrangeNodes :
                    OrangeNodes.append([round((i[0]+nearestNode[0])/2,2),round((i[1]+nearestNode[1])/2,2),i[2]])
        #plt.show()  
        return OrangeNodes

    def linePath(self,OrangeNodes:list,pos:list)->list:
    #best fit
        x = []
        y = []
        j=[]
        path = []
        #print(len(OrangeNodes))

        for i in range(len(OrangeNodes)):
            if OrangeNodes[i][1]<pos[1]:
                j=j+[i]
        j.reverse()
        for i in j:
            OrangeNodes.remove(OrangeNodes[i])
        if len(OrangeNodes)<1:
            return path
        for i in OrangeNodes:
            if i[1]>=pos[1]:
                x=x+[i[0]]
                y = y+[i[1]]
            if self.count<4:
                if self.origin[1] != 0:
                    end = self.origin[1]
                elif i[2]==2:
                    end = i[1]
                    break
            else:
                end = i[1]
        try:
            a, b = np.polyfit(np.array(x), np.array(y), 1)
        except:
            a=0
            b=0
        y = list(np.linspace(float(pos[1]),end,30))
        if a != 0:
            for i in y:
                path.append([(i-b)/a,i])
        else:
            for i in y:
                path.append([pos[0],i])
        return path

    def filter(self, arr: list) -> list:
        df = pd.DataFrame({'data': arr})
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1
        df_out = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
        return df_out['data'].tolist()

    def circle(self,points:list)->float:
        x,y,C = symbols('x y C')
        eq1 = Eq((x)**2 + (y)**2 - 2*points[0][0]*x - 2*points[0][1]*y + (points[0][0])**2 + (points[0][1])**2 - C, 0)
        eq2 = Eq((x)**2 + (y)**2 - 2*points[1][0]*x - 2*points[1][1]*y + (points[1][0])**2 + (points[1][1])**2 - C, 0)
        eq3 = Eq((x)**2 + (y)**2 - 2*points[2][0]*x - 2*points[2][1]*y + (points[2][0])**2 + (points[2][1])**2 - C, 0)
        sol = solve([eq1, eq2, eq3], (x, y, C))
        x0 = sol[0][0]
        y0 = sol[0][1]
        r = math.sqrt(sol[0][2])
        return x0,y0,r

    def meanCircles(self,outerCones:list,innerCones:list)->float:
        #six variables with six equation (x-x0)^2 + (y-y0)^2 = R^2, (x-x0)^2 + (y-y0)^2 = r^2
        x0=[]
        y0=[]
        r1=[]
        r0=[]
        for i in range(len(outerCones)-2):
            x,y,r = self.circle([outerCones[i],outerCones[i+1],outerCones[i+2]])
            x0 = x0+[x]
            y0 = y0+[y]
            r1 = r1+[r]
        for i in range(len(innerCones)-2):
            x,y,r = self.circle([innerCones[i],innerCones[i+1],innerCones[i+2]])
            x0 = x0+[x]
            y0 = y0+[y]
            r0 = r0+[r]
        x0 = self.filter(x0)
        y0 = self.filter(y0)
        r1 = self.filter(r1)
        r0 = self.filter(r0)
        x0 = sum(x0)/len(x0)
        y0 = sum(y0)/len(y0)
        r1 = sum(r1)/len(r1)
        r0 = sum(r0)/len(r0)
        reduisMean = (r1+r0)/2
        return x0,y0,reduisMean

    def circlePath(self,outerCones:list,innerCones:list,pos:list=[0,0])->list:
        path=[]
        x=[]
        y1=[]
        y2=[]
        x0,y0,Rm=self.meanCircles(outerCones,innerCones)
        if pos == [0,0] and outerCones[0][2]==3:
            pos = [x0-Rm,y0]
        elif pos == [0,0] and outerCones[0][2]==4:
            pos = [x0+Rm,y0]
        if round((pos[0]-x0),3) == 0:
            if pos[1] > y0:
                start = math.pi/2
            else:
                start = -math.pi/2
        else:
            start = math.atan(round((pos[1]-y0)/(pos[0]-x0),3))
        #print(outerCones)
        if outerCones[0][2]==3:
            if round((pos[0]-x0),3) < 0 and round((pos[1]-y0),3) < 0:     
                start = start - math.pi
            elif round((pos[0]-x0),3) < 0 and round((pos[1]-y0),3) >= 0:
                start = start + math.pi
            seta=list(np.linspace(start,-math.pi,30))
            for i in seta:
                x.append(Rm*math.cos(i)+x0)
                if i < 0:
                    y2.append(-math.sqrt(round(Rm**2-(x[-1]-x0)**2,3))+y0)
                    #print(i,x[-1],y2[-1])
                else:
                    y1.append(math.sqrt(round(Rm**2-(x[-1]-x0)**2,3))+y0)
                    #print(i,x[-1],y1[-1])
        else:
            if start < 0:
                start = start + 2*math.pi
            if round((pos[0]-x0),3) < 0 and round((pos[1]-y0),3) < 0:     
                start = start + math.pi
            elif round((pos[0]-x0),3) < 0 and round((pos[1]-y0),3) >= 0:
                start = start - math.pi
            seta=list(np.linspace(start,2*math.pi,30))
            for i in seta:
                x.append(Rm*math.cos(i)+x0)
                if i > math.pi:
                    y2.append(-math.sqrt(round(Rm**2-(x[-1]-x0)**2,3))+y0)
                    #print(i,x[-1],y2[-1])
                else:
                    y1.append(math.sqrt(round(Rm**2-(x[-1]-x0)**2,3))+y0)
                    #print(i,x[-1],y1[-1])
        
        for i in range(len(y1)):
            path.append([x[i],y1[i]])
        for i in range(len(y2)):
            path.append([x[i+len(y1)],y2[i]])
        
        return path

    def counter(self,pos:list,bigOrange:list):
        counter_OrangeNodes=self.OrangeNodes(bigOrange)
        #self.get_logger().info(f'self.state.pose.pose.position.x,self.state.pose.pose.position.y is {self.state.pose.pose.position.x,self.state.pose.pose.position.y} ')
        #self.get_logger().info(f'self.pastPos[0],self.pastPos[1] is {self.pastPos[0],self.pastPos[1]} ')
        if self.origin == [0,0]:
            if len(counter_OrangeNodes)<1:
                return 0
            else:
                if (pos[1]>counter_OrangeNodes[0][1]) and (self.pastPos[1]<counter_OrangeNodes[0][1]) and (round(pos[0],0) < round(counter_OrangeNodes[0][0]+2,0) and round(pos[0],0) > round(counter_OrangeNodes[0][0]-2,0)):
                    self.count=self.count+1
                    self.origin = counter_OrangeNodes[0]
        else:
            if (pos[1]>self.origin[1]) and (self.pastPos[1]<self.origin[1]) and (round(pos[0],0) < round(self.origin[0]+1,0) and round(pos[0],0) > round(self.origin[0]-1,0)):
                self.count=self.count+1
        self.get_logger().info(f'self.count is {self.count} ')
        if len(counter_OrangeNodes)==2:
            self.meanPoint = [(counter_OrangeNodes[0][0]+counter_OrangeNodes[1][0])/2,(counter_OrangeNodes[0][1]+counter_OrangeNodes[1][1])/2]
            self.origin = self.meanPoint
        
    def path(self,rightBlueCones:list,leftBlueCones:list,rightYellowCones:list,leftYellowCones:list,orangeCones:list,bigOrange:list)->list:
        
        path=[]
        pos=[self.state.pose.pose.position.x,self.state.pose.pose.position.y]
        orange=orangeCones+bigOrange
        orange.sort(key=lambda p: (p[0] - pos[0])**2 + (p[1] - pos[1])**2)
        #print(orange)
        OrangeNodes1 =self.OrangeNodes(orange)
        
        if len(bigOrange)>2:
            self.counter(pos,bigOrange)

        if self.count<1:
            path=self.linePath(OrangeNodes1,pos)
            if len(rightBlueCones)>3:
                path=path+self.circlePath(rightBlueCones,rightYellowCones)
        elif self.count<2:
            path=self.circlePath(rightBlueCones,rightYellowCones,pos)
            path=path+self.circlePath(rightBlueCones,rightYellowCones)
        elif self.count<3:
            path=self.circlePath(rightBlueCones,rightYellowCones,pos)
            if len(leftYellowCones)>=3 and len(leftBlueCones)>=3:
                path=path+self.circlePath(leftYellowCones,leftBlueCones)
        elif self.count<4:
            path=self.circlePath(leftYellowCones,leftBlueCones,pos)
            path=path+self.circlePath(leftYellowCones,leftBlueCones)
        elif self.count<5:
            path=self.circlePath(leftYellowCones,leftBlueCones,pos)
            if len(OrangeNodes1)>0 and pos[1]< self.origin[1]:
                path=path+self.linePath(OrangeNodes1,path[-1])
        elif self.count>=5:
            path=path+self.linePath(OrangeNodes1,pos)
        
        return path

    def getPath(self)->list:
        rightBlueCones,leftBlueCones,rightYellowCones,leftYellowCones,orangeCones,bigOrange = self.conesClassification()
        path = self.path(rightBlueCones,leftBlueCones,rightYellowCones,leftYellowCones,orangeCones,bigOrange)
        return path

def main(args=None):
    rclpy.init(args=args)
    path = SendPath()
    rclpy.spin(path)
    path.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()