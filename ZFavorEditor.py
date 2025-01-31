import pandas as pd
import json,os
import ZBaseFunc

from PySide2.QtUiTools  import QUiLoader
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

def LoadFavorListCfg(FavorList = QTreeWidget,CheckBox = None):

    FavorList.setColumnCount(2)
    FavorList.setHeaderLabels(('SYMBOL', 'POSITION', 'COMMENT'))

    FavorListFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultFavor.ZFfv'
    try:
        with open(FavorListFilePathName, 'r') as load_f:
            FavorDict = json.load(load_f)
        print('Load Default FavorList Config success!!')
    except:
        print('Load Default FavorList Config Fail!!')
        FavorDict = {
            "DEFAULT": [['AAPL','','']],
            'BLACKLIST': [['QT','','']]
        }
    FavorList.clear()
   # FavorList.setSelectionMode(QAbstractItemView.ExtendedSelection)
    for FLGroup, FLSymbol in FavorDict.items():
        root = QTreeWidgetItem(FavorList)
        root.setText(0, FLGroup)
        if CheckBox:
            root.setCheckState(0, Qt.Checked)
        elif CheckBox == False:
            root.setCheckState(0, Qt.Unchecked)
        for i in FLSymbol:
            child = QTreeWidgetItem(root)
            child.setText(0, i[0])
            child.setText(1, i[1])
            child.setText(2, i[2])
            if CheckBox:
                child.setCheckState(0, Qt.Checked)
            child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable|Qt.ItemIsUserCheckable)
    FavorList.addTopLevelItem(root)

    FavorList.setCurrentItem((FavorList.topLevelItem(0)))
    return

class FavorEditorUIProc:
    def __init__(self):
        self.FavorEditorUI = QUiLoader().load('UIDesign\FavorEditor.ui')
        self.FavorEditorUI.Input.textChanged.connect(self.HandleInputChanged)
        self.FavorEditorUI.ListFilter.doubleClicked.connect(self.HandleAddSymbol)
        self.FavorEditorUI.FavorList.itemDoubleClicked.connect(self.HandleFavorListDelete)
        self.FavorEditorUI.Save.clicked.connect(self.HandleSaveFavorList)
        self.FavorEditorUI.AddAll.clicked.connect(self.HandleAddAll)

        self.FavorEditorUI.FavorList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.FavorEditorUI.FavorList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)

    def FavorListChechboxSelectMenu(self):
        popMenu = QMenu()
        if self.FavorEditorUI.FavorList.currentItem().parent() == None:
            Move2BlackList  = popMenu.addAction("移入黑名单")
            Move2DefaultList  = popMenu.addAction('移入默认')

            Move2BlackList.triggered.connect(self.MoveSelectedList2BlackList)
            Move2DefaultList.triggered.connect(self.MoveSelectedList2DefaultList)
        popMenu.exec_(QCursor.pos())
        return

    def MoveSelectedList2BlackList(self):

        cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)
        TempMoveList = []
        for i in range(ChildCnt):
            TempMoveList.append(cursor.value().text(0))
            cursor = cursor.__iadd__(1)
        print(TempMoveList)

        cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList)
        while cursor.value():
            Temp = cursor.value()
            if(Temp.text(0) =='BLACKLIST'):
                break
            cursor = cursor.__iadd__(1)

        ChildCnt= Temp.childCount()
        cursor = cursor.__iadd__(1)
        BlackListSymbols = []
        for i in range(ChildCnt):
            BlackListSymbols.append(cursor.value().text(0))
            cursor = cursor.__iadd__(1)
        MoveList = []
        for one in TempMoveList:
            if one not in BlackListSymbols:
                MoveList.append(one)

        for Symbol in MoveList:
            child = QTreeWidgetItem()
            child.setText(0, Symbol)
            child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            Temp.addChild(child)






        return

    def MoveSelectedList2DefaultList(self):

        return

    def handleFavorEditor(self,SelectList=[],NewClass=''):

        self.FavorEditorUI.show()
        self.FavorEditorUI.ListFilter.setEditTriggers(QAbstractItemView.NoEditTriggers)
        LoadFavorListCfg(self.FavorEditorUI.FavorList)

        if(len(SelectList) == 0):

            NasdaqTickerList = pd.read_csv('Data\\00_Config\\NasdaqTickerList.csv', sep='|')
            NyseAmexTickerList = pd.read_csv('Data\\00_Config\\NyseAmexTickerList.csv', sep='|')

            Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['Q'])]
            SelectList.extend(Temp['Symbol'].tolist())
            Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['G'])]
            SelectList.extend(Temp['Symbol'].tolist())
            Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['S'])]
            SelectList.extend(Temp['Symbol'].tolist())

            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['A'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['N'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['P'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['Z'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['V'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())

        self.SelectList = SelectList

        self.HandleInputChanged()

        if(NewClass != ''):
            text, ok = QInputDialog.getText(self.FavorEditorUI, '创建新分类', '输入新分类名称:',text=NewClass)
            if ok and text != '':
                QtreeNodeList = ZBaseFunc.GetQtreeRootNode(self.FavorEditorUI.FavorList)
                if text in QtreeNodeList:
                    ZBaseFunc.Log2LogBox(text + ' class already exist in the favor list')
                    return
                root = QTreeWidgetItem(self.FavorEditorUI.FavorList)
                root.setText(0, text)

    def HandleItemText(self):
        print('fuck')

    def HandleInputChanged(self):

        VagueSymbol = self.FavorEditorUI.Input.text().upper()

        slm = QStringListModel()
        self.FliteredList=list(filter(lambda x: VagueSymbol in x, self.SelectList))
        slm.setStringList(self.FliteredList)
        self.FavorEditorUI.ListFilter.setModel(slm)

    def HandleAddAll(self):
        for Ticker in self.SelectList:
            self.HandleAddSymbol(Symbol = Ticker)

    def HandleAddSymbol(self,Symbol = None):
        if type(Symbol) != type('AAPL'):
            SelectedSymbol = self.FliteredList[self.FavorEditorUI.ListFilter.currentIndex().row()]
        else:
            SelectedSymbol = Symbol
        if (self.FavorEditorUI.FavorList.currentIndex().parent().row() != -1):
            cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList.currentItem().parent())
        else:
            cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)
        for i in range(ChildCnt):
            Temp = cursor.value()
            if Temp.text(0) == SelectedSymbol:
                return
            cursor = cursor.__iadd__(1)

        child = QTreeWidgetItem()
        child.setText(0, SelectedSymbol)
        child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        if (self.FavorEditorUI.FavorList.currentIndex().parent().row() != -1):
            self.FavorEditorUI.FavorList.currentItem().parent().addChild(child)
        else:
            self.FavorEditorUI.FavorList.currentItem().addChild(child)

    def HandleFavorListDelete(self,item,colume):

        if(colume == 0):
            currNode = self.FavorEditorUI.FavorList.currentItem()
            if (self.FavorEditorUI.FavorList.currentIndex().parent().row() == -1):
                if (self.FavorEditorUI.FavorList.currentItem().text(0) != 'DEFAULT' and
                    self.FavorEditorUI.FavorList.currentItem().text(0) != 'BLACKLIST'):
                    self.FavorEditorUI.FavorList.takeTopLevelItem(self.FavorEditorUI.FavorList.indexOfTopLevelItem(currNode))
                else:
                    text, ok = QInputDialog.getText(self.FavorEditorUI, '添加分类', '输入新的分类名:')
                    if ok:
                        QtreeNodeList = ZBaseFunc.GetQtreeRootNode(self.FavorEditorUI.FavorList)
                        if text in QtreeNodeList:
                            ZBaseFunc.Log2LogBox(text + ' class already exist in the favor list')
                            return
                        root = QTreeWidgetItem(self.FavorEditorUI.FavorList)
                        root.setText(0, text)

            else:
                TempParent = currNode.parent()
                TempParent.removeChild(currNode)


    def HandleSaveFavorList(self):
        FavorDict=dict()
        cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList)
        while cursor.value():
            Temp = cursor.value()
            print(self.FavorEditorUI.FavorList.indexOfTopLevelItem(Temp))
            print(Temp.text(0))
            if self.FavorEditorUI.FavorList.indexOfTopLevelItem(Temp) != -1:
                GroupLabel= Temp.text(0)
                FavorDict[GroupLabel] = []
            else:
                FavorDict[GroupLabel].append([Temp.text(0),Temp.text(1),Temp.text(2)])

            cursor = cursor.__iadd__(1)

        FavorListFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultFavor.ZFfv'
        with open(FavorListFilePathName, "w") as f:
            json.dump(FavorDict, f)
        pass

