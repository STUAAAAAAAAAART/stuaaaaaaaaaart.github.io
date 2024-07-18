---
parent: 2024
layout: page
title: ZZ-Journal24-003-duplicate
date: 2024-07-13 00:00:00 +0800
---

# duplicating a subsection of a joint chain

**goal**: get two joints of a joint hierachy; duplicate all joints between them, including those two joints

**problem**: <br/>
https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/CommandsPython/duplicate.html

`cmds.duplicate()` does not have an option to duplicate specifically between two specified objects

**so**: script......

important: DAG names in this operation are all handled in full, not using shortnames (just because the longNames is almost always guaranteed to point to a unique DAG object and not a possible similarly-named object)

example:
```md
joint0
  ↳ joint1 ⬅ start
    ↳ joint2a
	| ↳ joint3
	|   ↳ joint4 ⬅ end
	|     ↳ joint5 ⚠
	|       ↳ joint6
	|        ↳ joint7
	↳ joint2b ⚠
	  ↳ joint3
	    ↳ joint4
	      ↳ joint5
	        ↳ joint6
	         ↳ joint7

note: example and worst case purposes, i usually try to not shortname objects identically

start:
'joint0|joint1'

end:
'joint0|joint1|joint2a|joint3|joint4'

⚠ branches to not duplicate:
'joint0|joint1|joint2b'
'joint0|joint1|joint2a|joint3|joint4|joint5'

desired outcome:
'joint0|joint1duplicated'
'joint0|joint1duplicated|joint2a'
'joint0|joint1duplicated|joint2a|joint3'
'joint0|joint1duplicated|joint2a|joint3|joint4'
```

> 

- get two endpoints
- see if one is parent of another
	- `listRelatives(ad=True)` (list all descendants)
	- find if either is in list of other
- if valid, crawl list of children towards "youngest" object
	- `listRelatives(ad=False)`
	- `deleteList=[]` make a list of objects not leading to desired object
		- note that list is of `string` to DAG objects with full names
		- note that objects belong to the existing item and needs to be pointed to the new duplicated one
- add descendants of desired object to `deleteList`
- duplicate "oldest" desired object normally
- resilver list to update to descendants of new list
	- note: if this isn't done, the previous objects will be deleted instead
- `mc.delete()` objects in `deleteList` 
	- pruning anything that is not strictly between the two endpoints

**postscript**:
- all DAG path query actions are done through `cmds`, but it got the job done and converting them to `openmaya` commands would be a little more work. would still want to do this via `openmaya` next time just for the heck of it
- might want to convert this script so it adds all objects between the 2 selected objects to the scene selection list and not run the duplication actions, for the purpose for selection convenience and passing to other functions
- might also want to sanatise the script to account for using this for any outliner object, not just object that are joints 

## script

note: script is for the maya shelf

```py
import maya.cmds as mc
import maya.api.OpenMaya as om2

"""
playlist while coding:
	https://www.youtube.com/watch?v=4OkmCjoMkyg
	https://www.youtube.com/watch?v=9mRYUVQcLW0
"""

# DUPLICATE HIERARCHY SECTION
# NOT CONTAINER SAFE FOR OPENMAYA, CAST OBJECTS TO om2.MSelectionList BEFORE RETURNING IF USED ELSEWHERE

"""TODO:
- check for and retain associated shape nodes (in case this function is used elsewhere in the DAG outliner that's not joints)
- make hyper-sanitised version that only work for joints?
"""

activeSelection = om2.MGlobal.getActiveSelectionList()


# only allow 2 objects in active selection
	# listen i don't want to add in more stuff right now like ABABAB paired-multi-operations 
if len(activeSelection.getSelectionStrings()) != 2: # has to be 2
	raise ValueError (f"DupHierSection - selection not exactly 2: {activeSelection.getSelectionStrings()}")

# test for DAG (i.e. on the outliner)
for i in [0,1]:
	try:
		activeSelection.getDagPath(i)
	except:
		raise ValueError(f"DupHierSection - object is not a DAG node: {activeSelection.getSelectionStrings(i)}")

# test if one is child of other
twoSelection = list(activeSelection.getSelectionStrings()) # expect 2 DAG paths

# is A parent of B?
oldParent = mc.ls(twoSelection[0],long=True)[0]
oldRelatives = mc.listRelatives(oldParent, ad=True, f=True)
oldTarget = mc.ls(twoSelection[1],long=True)[0]

firstCheck = False

try:
	finDex = oldRelatives.index(oldTarget)
		# in list: return integer index
		# not in list: python list.index() raise valueError
	firstCheck = True
except:
	oldParent = mc.ls(twoSelection[1],long=True)[0]
	oldRelatives = mc.listRelatives(oldParent, ad=True, f=True)
	oldTarget = mc.ls(twoSelection[0],long=True)[0]

if firstCheck == False:
	# A not parent of B
	# is B parent of A?
	try:
		finDex = oldRelatives.index(oldTarget)
		firstCheck = True
	except: # A and B are cousins or not under same ancestor object
		raise ValueError(f"DupHierSection - selection not direct desendants: {twoSelection}")

# prepare for runtime
toDelete = []

checker = oldParent
# go down list
while True:
	loopAround = False
	# target object is guaranteed to be in subhierarchy due to earlier checks
	
	# get immediate children
	checkList = mc.listRelatives(checker, ad=False, f=True)
	
	try:
		# check if any children is target
		# if one is: add others to delete list and break
		getTarget = checkList.index(oldTarget) #RAISE: oldTarget is not in List
		# passed: target IS in list (may contain other objects)
		fillList = checkList.copy()
		fillList.pop(getTarget)
		toDelete.extend(fillList)
		# wrapup: get immediate children and add to delete list
		# remember it's just objects between A and B, anything past that is not wanted
		fillList  = mc.listRelatives(oldTarget, ad=False, f=True)
			# RETURN: [list] if >0, None if empty
		if fillList != None:
			# TODO: sanitise for shape lists
			# TODO: hyper-sanitise for joints only?
			toDelete.extend(fillList)
		break

	except:
		# item not found, find child's decendants for target
		# again, target object is guaranteed to be in subhierarchy due to earlier checks, but if i must...
		for item in checkList:
			childEnum = mc.listRelatives(item, ad=True, f=True) #allDesendants

			try:
				childEnum.index(oldTarget) #RAISE: oldTarget is not in List
				# this child has target in descendants
				# get other items and add to toDelete list
				getTarget = checkList.index(item)
				fillList = checkList.copy()
				fillList.pop(getTarget)
				toDelete.extend(fillList)
				# recurse while loop
				checker = item
				loopAround = True
				# odd, why doesn't a continue here return to top of while loop
			except:
				pass
		# end forLoop
	if loopAround:
		continue
	else:
		# if somehow everything has fallen through (oh wow??)
		raise ValueError(f"DupHierSection - crawl failed, troubleshoot: {twoSelection}")


# runtime

# duplicate
newParent = mc.ls(
	mc.duplicate(oldParent)[0],
	long=True
	)[0]
# note: ensure renameChildren (rc) is False, as the script requires the relative naming 
# MAYA 2022: mc.duplucate() has a flag (f) for returning full DAG path names, without the need to mc.ls(long=True)
#	https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/CommandsPython/duplicate.html

# replaces delete list items with new parent DAG path
for i in range(len(toDelete)):
	toDelete[i] = toDelete[i].replace(oldParent,newParent,1)

# mc.delete new items not in sub-hierachy
mc.delete(*toDelete) # reminder: python list *unpacking for functions: https://www.w3schools.com/python/python_tuples_unpack.asp
```