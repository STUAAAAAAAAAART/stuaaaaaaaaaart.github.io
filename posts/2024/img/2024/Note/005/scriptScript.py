import maya.cmds as mc
import maya.api.OpenMaya as om2

"""
playlist while coding:
	https://www.youtube.com/watch?v=smyqDlcHE14
	https://www.youtube.com/watch?v=1bEv74JrHQo
"""

# selection phase: get items

activeSelection = om2.MGlobal.getActiveSelectionList()

# [2022: NOT IN USE] convert shortName string from getSelectionStrings to longnames (just because)
# checkList = mc.ls(activeSelection.getSelectionStrings(), long=True) # -> list : ["longName", ... ]
	# line not in use because mc.listConnections() does not return longNames.
		# the flag to return longNames exist from 2023 onward

# detection phase: get all connections strictly within selection

checkList = activeSelection.getSelectionStrings() # -> list : ["shortName", ... ]

nodeList = []
addAttrList = []
connectionList = []
nodeCounter = 0
for node in checkList:
	# write createNode commands
	nodeList.append(f'nodeList[{nodeCounter}] = mc.createNode("{mc.nodeType(node)}", n="{node}", skipSelect = True)')

	# check for user-defined attributes and write addAttr commands
	checkAttrUD = mc.listAttr(node, userDefined=True)
		# WARNING: returns noneType if list is empty
	if checkAttrUD: # if not None, basically
		for attr in checkAttrUD:
			# query custom attr type
			checkAttrType = mc.attributeQuery(attr, n=node, attributeType = True)
			if checkAttrType in ["float","double","byte","short","long","char"]:
			# query attribute attributes (:shrug:)
				flagString = ""
				# default value
				flagString += f", defaultValue = {mc.attributeQuery(attr, n=node, listDefault = True)[0]}"
				# soft range (attribute sliders)
				if mc.attributeQuery(attr, n=node, softMinExists = True):
					flagString += f", hasSoftMinValue = True, "
					flagString += f", softMinValue = {mc.attributeQuery(attr, n=node, softMin = True)}"
				if mc.attributeQuery(attr, n=node, softMaxExists = True):
					flagString += f", hasSoftMaxValue = True, "
					flagString += f", softMaxValue = {mc.attributeQuery(attr, n=node, softMax = True)}"
				# hard range (hard limits)
				if mc.attributeQuery(attr, n=node, minExists = True):
					flagString += f", hasMinValue = True, "
					flagString += f", minValue = {mc.attributeQuery(attr, n=node, softMin = True)}"
				if mc.attributeQuery(attr, n=node, minExists = True):
					flagString += f", hasMaxValue = True, "
					flagString += f", maxValue = {mc.attributeQuery(attr, n=node, softMin = True)}"
				# hidden?
				holdBool = mc.attributeQuery(attr, n=node, hidden = True)
				flagString += f", hidden = {'True'*holdBool}{'False'*(not holdBool)}"
				# connection settings
				holdBool = mc.attributeQuery(attr, n=node, readable = True)
				flagString += f", readable = {'True'*holdBool}{'False'*(not holdBool)}"
				holdBool = mc.attributeQuery(attr, n=node, writable = True)
				flagString += f", writable = {'True'*holdBool}{'False'*(not holdBool)}"
				# animatable?
				holdBool = mc.attributeQuery(attr, n=node, keyable = True)
				flagString += f", keyable = {'True'*holdBool}{'False'*(not holdBool)}"

				# write attAttr command
				addAttrList.append( f'mc.addAttr("{node}", longName = "{attr}", attributeType = "{checkAttrType}" {flagString})')
			else:
				# complex attribute, manual consideration required for now
					# it should be surmountable within mc., but that's for another time as other utilities come
				# TODO: other types:
					# enum
						# listEnum = True 
					# compound
						# listChildren = True
						# listSiblings = True
				addAttrList.append(f'# "{checkAttrType}" type: {node}.{attr}')
			
	# query outgoing connections

	queryConnections = mc.listConnections(node, s=False, c=True,  d=True, p=True )  # -> list : ["shortName_from.attr", "shortName_to.attr", ... , ... ]
		# downstream command
	for i in range(int(len(queryConnections)*0.5)): # -> "shortName_from.attr"
		# note: script has been working with shortnames the whole time,
		# ensure node names are all consistently shortNames or longNames (and not a mix of both)
		if queryConnections[i+i+1].split('.')[0] in checkList: # <- "shortName_to.attr"
			# downstream node is in selection scope, append [input, output] to list
			holdIndex = checkList.index(queryConnections[i+i+1].split('.')[0])
			fromNode = f'f"{{nodeList[{nodeCounter}]}}.{queryConnections[i+i  ].split(".")[1]}"'
			toNode   = f'f"{{nodeList[{holdIndex  }]}}.{queryConnections[i+i+1].split(".")[1]}"'
			#f'f"{{nodeList[{index}]}}.{attr}"', f'f"{{nodeList[{index}]}}.{attr}"'
			
			# write connectAttr commands
			connectionList.append(f'mc.connectAttr({fromNode}, {toNode}) # {queryConnections[i+i]} -> {queryConnections[i+i+1]}')
			
	# next node
	nodeCounter += 1

# print phase: print all commands for creation and connections
# TODO: write text to file (honestly copying from the script editor will do for now)


print("\n# scripterStu: start print\n")

print("import maya.cmds as mc")
print("import maya.api.OpenMaya as om2\n")

print("activeSelection = om2.MGlobal.getActiveSelectionList()")

print("\n# create nodes\n")
print(f"nodeList = list(range({len(checkList)}))\n")

for printOut in nodeList:
	print(printOut)
print("\n# custom attributes\n")
for printOut in addAttrList:
	print(printOut)
print("\n# connect attributes\n")
for printOut in connectionList:
	print(printOut)

print(f"\n# scripterStu: print done\n")