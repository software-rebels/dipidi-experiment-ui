import pickle
import sys
import os

sys.path.append(os.path.dirname(__file__))


def getHashKey(funcName, fileName):
    return f"{funcName};{fileName}"


class FuncEntity:
    lookup = dict()
    loaded = False

    def __init__(self, name, fileName):
        self.name = name
        self.fileName = fileName
        self.dependsBy = set()

    @classmethod
    def get(cls, funcName, fileName):
        return cls.lookup[getHashKey(funcName, fileName)]

    @classmethod
    def getOrCreate(cls, funcName, fileName):
        if not getHashKey(funcName, fileName) in cls.lookup:
            cls.lookup[getHashKey(funcName, fileName)] = FuncEntity(funcName, fileName)
        return cls.get(funcName, fileName)

    def addDependBy(self, fEntity):
        self.dependsBy.add(fEntity)

    def getDependsBy(self):
        return self.dependsBy

    # def __repr__(self):
    #    return getHashKey(self.name, self.fileName)

    # def __hash__(self):
    #    return hash(repr(self))


def loadData(pkl_path):
    if not FuncEntity.loaded:
        f = open(pkl_path, 'rb')
        FuncEntity.lookup = pickle.load(f)
        f.close()
        FuncEntity.loaded = True


def dfs(node: FuncEntity, seen=None):
    if seen is None:
        seen = set()
    answer = set()
    answer.add(node)
    for child in node.getDependsBy():
        if child not in seen:
            seen.add(child)
            answer.update(dfs(child, seen))
    return answer


def findImpactedFiles(node: FuncEntity):
    impactedEntities = dfs(node)
    impactedFiles = set()
    for ent in impactedEntities:
        impactedFiles.add(ent.fileName)
    return impactedFiles
