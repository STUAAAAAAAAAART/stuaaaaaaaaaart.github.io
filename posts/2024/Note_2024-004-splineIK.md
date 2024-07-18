---
parent: 2024
layout: page
title: ZZ-Journal24-004-splineIK
date: 2024-07-13 00:00:00 +0800
---

# Spline IK thoughts

⚠ this isn't done yet, just had a thought that challenged how i saw the splineIK solver and how i used it in the past, and am in the middle of testing something

goal of spline IK:
- reduce the amount of controls along a long joint chain
- control a joint chain through controlling a curve
- localise the three general parts of moving a body: the shoulder/upper, the hip/lower, and the middle/center
	- going between poses centered around the top (e.g. climbing over the wall, lifting the hip up), and poses centered around the bottom (e.g. bending to touch the toes, lowering the torso down)

limitations of spline IK:
- payoff for setup complexity diminishes if joint chain is short
- joints flip if curve control points are moved to the other side of the object
	- specifically when the points are moved opposite to the 0th point in object space
	- this is mostly not an issue for most poses that do not need to reverse (or reverse but flipping is desired, e.g. bending down), but control is mostly lost to shape that behaviour
	- rotating the object before the curve's deformers kind of kicks the problem-can down the road

aforementioned challenge:
- rigging other types of IK (3-joint IK) are usually done in place local to the joints being driven (e.g. the IK arm is in the same place as the FK/character's arm)
	- this is a harder thing to address and stick to, when moving the curve that drives the IK would add additional transforms to the IK driver joints
- the spline IK heavily rely on the curve that drives it, and controlling that curve is through deforming or skinning the curve by other objects
	- this is very similar to the concept of skinning a mesh to a skeleton...

----
<br/>
<p align="center"> so... if moving the curve affects the spine IK driver joints in an extraneous way, why am i hellbent on getting the curve to be in place local to the driven joint chain?
</p>

----

i'm in the middle of testing an implementation that's new to me, and re-evaluating past rigs that utilised the previous spline IK to some success (especially the foot rig of the spinosaurus rig), so that will be a thing i have to explain later

it'd involve treating the driver curve like the skinned mesh and not moving it away from its creation position, and driving the IK joint chain "remotely" (i.e. plugging translate/rotate/scales without bringing the spline IK logic to the root of the joint chain)

a preview curve could be duplicated for visual feedback, but the source curve would be hidden along with the rig logic group

EDIT: the title used to be called "Spline IK and the Online Resources": i'm still working on the note that tracks all the methods being posted online out of curiosity, as this solver still feels like a dark art of sorts to me even today
