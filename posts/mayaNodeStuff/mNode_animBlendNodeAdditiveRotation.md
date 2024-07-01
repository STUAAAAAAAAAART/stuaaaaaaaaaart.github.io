---
parent: Maya Node Notes
title: animBlendNodeAdditiveRotation
layout: page
---

# animBlendNodeAdditiveRotation Node

https://download.autodesk.com/us/maya/2010help/Nodes/animBlendNodeAdditiveRotation.html

https://help.autodesk.com/cloudhelp/2023/ENU/Maya-Tech-Docs/Nodes/animBlendNodeAdditiveRotation.html

earliest known version: 2010

## goal: add two rotations together

notes:
- maya has a specific type of foating point attribute for rotations (`doubleAngle`)
- any connections from a `doubleAngle` to a plain numeric attribute will result in the creation of an intermediary `unitConversion` Node, which multiplies `pi` or its reciprocal of to the attribute depending on connection direction
	- this behaviour is not present when the project or scene has rotation units set to `RADIANS`

solution 1:
> rotation ➡ `composeMatrix` ➡ `multMatrix` ➡ `decomposeMatrix` ➡ rotation
- prevents unitConversion
- single-equation behaviour reduces number of nodes in the file (see comparison to solution 2)
- negative of a rotation requires intermediary `inverseMatrix` node
- quaternion in matrix, which means results are of `-180 < x < 180`
	- if an angle of 270 is needed, this is unfortunately not the way

solution 2:
> rotation ➡ `animBlendNodeAdditiveRotation` ➡ rotation
- prevents unitConverson
- subtraction and multiplication handled by weight attributes within
- single-operation behaviour unfortunately means one node is required between two rotations (i.e. for summing `n` number of rotations, a `triangle(n)` of addRotate nodes is needed)
- allows for component-wise or quaternion-based operation, depending on use case

## a use of this node

- a spline IK solver includes a `roll` and `twist` attribute, which spins joints about the curve axis.
	- `twist`ing interpolates all the joints between the start and end
	- if the floatAngle value is limited (e.g. parsed as a quaternion at any point in the evaluation chain) and given to the `twist` attribute, an intended rotation of 270 will end up being a rotation of -90, which causes the chain to `twist` the other way

## wishlist for maya
- make separate simple maths nodes for operations on floatAngle
	- i am not sure if there is some underlying thing to the `animBlendNode-` part of `animBlendNodeAdditiveRotation`, or it's really doing what it's doing just with a really really long name
- make a matrix node that weighs-up transforms (without scaling up the W-component like how the `passMatrix` would)
	- currently the `blendMatrix` node servers this purpose, but is very overkill for its purpose