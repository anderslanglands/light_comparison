## Quantities
Previously, UsdLux was rather vague about the exact quantities being emitted from lights, relying on implementing renderers doing the "obvious thing". This led to significant differences between the output of different renderers from the same USD layer. 

This updated spec makes explicit the quantities involved, as well as the form of the shaping functions so that users can reliably port lighting setups from one renderer to another. It is espected that a renderer interfacing with USD will follow this specification exactly. The repository at [REPO] provides a selection of simple test scenes along with example images to be used for validation.

In particular, unless otherwise specified, lights' emission is assumed to be parameterized in _nits_. This emission is calculated directly from the `inputs:intensity` and `inputs:exposure` attributes _before_ the application of the `inputs:color` attribute, textures and shaping functions. 

```
emission = intensityAttr * pow(2, exposureAttr)
            * normalizeAttr ? NormalizeFactor() : 1
            * colorAttr
            * enableColorTemperatureAttr ?  Blackbody(colorTemperatureAttr) : color(1)
            * FocusFactor()
            * IesFactor()
            * ConeFactor()
```

## 2 UsdLuxLightAPI

### 2.1 GetIntensityAttr()
Scales the brightness of the light linearly. `inputs:intensity`, combined with `inputs:exposure`, specifies the emission of the light in $nit$. 
```
intensityAttr * pow(2, exposureAttr)
```

The luminance is specified _before_ the application of color, texture, shading functions and filters to the light. Thus a light with `inputs:intensity = 1`, `inputs:exposure = 0` and `inputs:color = [0.5, 0.3, 0.1]` would have an emission of `[0.5, 0.3, 0.1]` in an RGB renderer.

### 2.2 GetExposureAttr()
Scales the brightness of the light exponentially as a power of two, (similar to an f-stop contol over exposure). `inputs:exposure`, combined with `inputs:intensity`, specifies the emission of the light in $nit$. 

```
intensityAttr * pow(2, exposureAttr)
```

The luminance is specified _before_ the application of color, texture, shading functions and filters to the light. Thus a light with `inputs:intensity = 1`, `inputs:exposure = 0` and `inputs:color = [0.5, 0.3, 0.1]` would have an emission of `[0.5, 0.3, 0.1]` in an RGB renderer.

### 2.3 GetNormalizeAttr()
Scales the brightness of the light by the inverse of its world-space surface area, $A$, measured in scene units. 

```
NormalizeFactor = [](){ return 1 / A; }
```

Note that this area value is independent of the stage `metersPerUnit` metadata. Thus the behaviour of enabling this attribute on an area light is similar to, but not the same as, specifying the light's brightness in units of power. 

If the light is a distant light, the normalization factor should be calculated as the proportion of the hemisphere subtended by the cone with apex angle equal to the light's `inputs:angle` attribute, multiplied by $\pi$. Thus the `inputs:intensity` attribute specifies the emission of the light in terms of $lux$ recieved at a surface facing the light when `inputs:normalize` is enabled on a distant light.

```
NormalizeFactor = [](){ return M_PI / (1 - cos(angleAttr)); }
```

If the light is a dome light, `inputs:normalize` has no effect.


### 2.4 GetColorAttr()
Specifies the color of the emitted light as a tint factor

### 2.5 GetColorTemperatureAttr()
Specifies an additional color tint, T, to be applied to the emitted light when `inputs:enableColorTemperature == true`. The value of this attribute is measured in degrees Kelvin and is used to calculate the color tint using the normalized blackbody emission function in the rendering color space.

Thus if the rendering color space is sRGB and `inputs:colorTemperature = 6500.0`, the calculated color tint will be `[1, 1, 1]`.


## 3 UsdLuxShapingAPI

### 3.1 GetShapingFocusAttr()
Narrows the spread of the light by multiplying the emission by a shaping factor, $S$, that is calculated as the cosine of the angle between the emission direction, $\vec{\omega_e}$, and the light's $\vec{Z}$ axis, raised to the power of `inputs:shaping:focus`.

 ```
 FocusFactor = [](){ 
    float focus_factor = pow(dot(w_e, z), focus);
    return lerp(focusTint, color(1), focus_factor); 
 }
 ```

### 3.2 GetShapingFocusTintAttr()
Tints the emission in the focus falloff region. The default tint is black.

 ```
 FocusFactor = [](){ 
    float focus_factor = pow(dot(w_e, z), focus);
    return lerp(focusTint, color(1), focus_factor); 
 }
 ```

### 3.3 GetShapingIesNormalizeAttr()
Normalizes the IES profile so that it affects the shaping of the light while preserving the overall energy output.

