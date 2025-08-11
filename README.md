# Region-Quadtree
A region quadtree used specifically for image compression.

The program uses a given image. That image is then divided into four quadrents.
Each quadrant has an averaged color based on the colors in the given image. The 
quadrents are then divided further untill the quadrants error is less than or 
equal to an error threshold. This process is then repeated N times untill all 
quadrents have an error less than the error threshold or reach the max depth of
the tree.

You read more about how this works in my article [here](https://medium.com/@tannerwyork/quadtrees-for-image-processing-302536c95c00)


## Examples

![Compressing Starry Night](https://github.com/TannerYork/Region-Quadtree/blob/master/Images/starry_night_compression.gif)
![Compressing Wall-E](https://github.com/TannerYork/Region-Quadtree/blob/master/Images/wall-e_compression.gif)
