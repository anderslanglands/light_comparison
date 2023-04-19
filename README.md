# Problem Statement

Different renderers produce very different images for the same USD due to differences in how certain lights are interpreted. For example, here's Intel's Moore Lane scene rendered in Karma, Arnold and RTX:

![Moore Lane rendered in Solaris/Karma](renders/moore-lane/moore-lane_karma.jpg)
![Moore Lane rendered in Solaris/Arnold](renders/moore-lane/moore-lane_arnold.jpg)
![Moore Lane rendered in USD Composer/RTX Interactive](renders/moore-lane/moore-lane_rtx.jpg)

The issue here is that each renderer has its own interpretation of the quantity to be emitted given a particular parameterization of the distant light representiong the sun. Karma appears to be emitting nits when normalize is off and "lux at a patch facing the light" when normalize is on. Arnold and RTX both ignore the normalize flag, and RTX is essentially emitting "pi * lux". RIS does something else entirely:

![Comparison of a distant light illuminating a sphere](renders/distant_comparison.jpg)

# Solution
We need to update UsdLux to specify exactly what quantities should be emitted for each light and combination of its attributes so that lighting can be shared between applications and renderers.


# High-Level Plan
- [ ] Form working group with major rendering authors and users to decide on specification
- [ ] Enumerate all combinations of lighting attributes that affect the output and create contact sheets to show differences in implementation
- [ ] Reach consensus on what the implementation should be
- [ ] Draft a documentation update and/or new USD lighting Schema according to the decided specification
- [ ] Merge to USD
- [ ] Render happily ever after

# Contents of This Repository

## `renders`
Directory containing source renders for each scene/attribute combination, for each renderer

## `light_comparison.nk`
Nuke script used to generate the contact sheet images

## `light_comparison.hip`
Houdini project used to create USDs for testing, and to perform comparison renders in Solaris of Karma and Arnold (and eventually RIS hopefully). That was used to generate the following USD layers:

###  `cylinder-light-plane.usda` 
A cylinder light of length 1, radius 0.5 and intensity 30, 2 units above an 0.18-grey plane with the camera facing perpendicular to the plane.

![Cylinder light contact sheet](cylinder-light.jpg)

#### Observations
- Karma, Arnold and RTX appear to match

###  `disk-light-plane.usda` 
A disk light of radius 0.5, and intensity 30, 2 units above and directly facing an 0.18-grey plane with the camera facing perpendicular to the plane.

![Disk light contact sheet](disk-light.jpg)

#### Observations
- Karma, Arnold and RTX appear to match

###  `distant-light-plane.usda` 
A distant light of intensity 5, directly facing an 0.18-grey plane with the camera facing perpendicular to the plane.

![Distant light contact sheet](distant-light.jpg)

#### Observations
- RTX and Arnold maintain brightness regardless of `angle` and `normalize`
- RTX is `pi` times brighter than Arnold and Karma
- Karma's brightness changes with `angle` when `normalize=0`
- RIS uses a very different mapping of `intensity` to emitted luminance

###  `rect-light-plane.usda` 
A rect light of intensity 10, 1 unit above and directly facing an 0.18-grey plane with the camera facing perpendicular to the plane.

![Rect light contact sheet](rect-light.jpg)

#### Observations
- Arnold appears to ignore `focus` on a rect light
- Karma and RTX appear to match

###  `rect-light-plane_rotated.usda` 
A rect light of intensity 10, 1 unit above and rotated at 45 degrees to an 0.18-grey plane with the camera facing perpendicular to the plane. Used to test shaping controls.

![Rect spot, focus 0 contact sheet](rect-light_spot_focus-0.jpg)
![Rect spot, focus 10 contact sheet](rect-light_spot_focus-10.jpg)

#### Observations
- Arnold appears to ignore the spotlight controls on a rect light (but does respect them on a sphere light, see below).
- RTX ignores `focus` when spotlight shaping is enabled.
- RTX and Karma's mapping for `softness` is very different.
- RIS seems to interpret `coneAngle` much differently than the others.

###  `sphere-light-plane.usda` 
A sphere light of radius 0.5, and intensity 30, 2 units above an 0.18-grey plane with the camera facing perpendicular to the plane.

![Sphere light contact sheet](sphere-light.jpg)

#### Observations
- Karma and RTX have the same normalization, Arnold is different

###  `sphere-light-plane_rotated.usda` 
A sphere light of radius 0.5, and intensity 30, 2 units above and rotated at 45 degrees to an 0.18-grey plane with the camera facing perpendicular to the plane. Used to test shaping controls.

![Sphere spot, focus 0 contact sheet](sphere-light_spot_focus-0.jpg)
![Sphere spot, focus 10 contact sheet](sphere-light_spot_focus-10.jpg)

#### Observations
- Karma appears to expect `softness` in [0, 1], while RTX uses a different mapping that can go above 1 and produces different results for the same value. Arnold's mapping appears most similar to RTX.
- Arnold's result with `softness` 0 has a very hard edge at the boundary of the cone, while Karma and RTX have a softer edge.
- RTX and Karma look like they ignore `focus` when `coneAngle` is set, while Arnold does the opposite and ignores spotlight shaping when `foc`us` is set to non-zero.
- Karma looks like it ignores `coneAngle` in the range [90, 180] on the sphere light.
- RIS seems to interpret `coneAngle` much differently than the others.

### `dome-light.usda`
A dome light with intensity 1 and default transform using a coloured grid texture, illuminating a perfectly specular metallic sphere with the camera facing the sphere from 6 units along the +Z axis.

![Dome light texture](dome.jpg)

![Dome light contact sheet](dome-light.jpg)

#### Observations
- Karma and Arnold appear to match in terms of mapping on the dome. 
- For this texture, Arnold interprets `format=automatic` as `angular`, and had to be set manually to `latlong`
- Arnold appears to ignore `metallic` and `roughness` attributes of the UsdPreviewSurface
- RTX has a different mapping of the latlong texture from the others
