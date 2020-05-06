from PIL import Image, ImageDraw

PADDING = 1
OUTPUT_SCALE = 1
ERROR_THRESHOLD = 10


def weighted_average(hist):
    """Returns the weighted color average and error from a hisogram of pixles"""
    total = sum(hist)
    value = sum(i * x for i, x in enumerate(hist)) / total
    error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
    error = error ** 0.5
    return value, error


def color_from_histogram(hist):
    """Returns the average rgb color from a given histogram of pixle color counts"""
    r, re = weighted_average(hist[:256])
    g, ge = weighted_average(hist[256:512])
    b, be = weighted_average(hist[512:768])
    e = re * 0.2989 + ge * 0.5870 + be * 0.1140
    return (int(r), int(g), int(b)), e


class QuadtreeNode(object):
    """Node for Quadtree that holds a subsection of an image and 
        information about that section"""

    def __init__(self, img, box, depth):
        self.box = box  # (left, top, right, bottom)
        self.depth = depth
        self.children = None  # tl, tr, bl, br
        self.leaf = False

        # Gets the nodes average color
        image = img.crop(box)
        self.width, self.height = image.size  # (width, height)
        hist = image.histogram()
        self.color, self.error = color_from_histogram(hist)  # (r, g, b), error

    def is_leaf(self):
        """Determins if a the node is a leaf"""
        return self.leaf


class Quadtree(object):
    """Tree that has nodes with at most four child nodes that hold 
        sections of an image where there at most n leaf nodes where
        n is the number of pixles in the image"""

    def __init__(self, image, max_depth=7):
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self.width, self.height = image.size
        self.max_depth = max_depth
        self._build_tree(image, self.root, max_depth)

    def _build_tree(self, image, node, max_depth, curr_depth=0):
        """Recursively adds nodes untill max_depth is reached or error is less than 5"""
        if curr_depth >= max_depth or node.error <= ERROR_THRESHOLD:
            node.leaf = True
            return

        boxes = self._split(image, node.box)
        node_children = [QuadtreeNode(image, box, curr_depth+1)
                         for box in boxes]
        for child in node_children:
            self._build_tree(image, child, max_depth, curr_depth+1)
        node.children = node_children

    def _split(self, image, box):
        """Splits the given image section into four equal image boxes"""
        l, t, r, b = box
        lr = l + (r - l) / 2
        tb = t + (b - t) / 2
        tl = (l, t, lr, tb)
        tr = (lr, t, r, tb)
        bl = (l, tb, lr, b)
        br = (lr, tb, r, b)
        return [tl, tr, bl, br]

    def get_leaf_nodes(self, depth):
        """Gets all the nodes on a given depth/level"""
        if depth > self.max_depth:
            raise ValueError('A depth larger than the trees depth was given')

        leaf_nodes = []
        self._get_leaf_nodes_recusion(self.root, depth, leaf_nodes.append)
        return leaf_nodes

    def _get_leaf_nodes_recusion(self, node, depth, func):
        """Recusivley gets leaf nodes based on whether a node is a leaf or the given depth is reached"""
        if node.leaf is True or node.depth == depth:
            func(node)
        elif node.children is not None:
            for child in node.children:
                self._get_leaf_nodes_recusion(child, depth, func)

    def _create_image_from_depth(self, depth):
        """Creates a Pillow image object from a given level/depth of the tree"""
        m = OUTPUT_SCALE
        dx, dy = (PADDING, PADDING)  # padding for each image section
        image = Image.new('RGB', (self.width * m + dx, self.height * m + dy))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width * m + dx,
                        self.height * m + dy), (0, 0, 0))

        leaf_nodes = self.get_leaf_nodes(depth)
        for node in leaf_nodes:
            l, t, r, b = node.box
            box = (l * m + dx, t * m + dy, r * m - 1, b * m - 1)
            draw.rectangle(box, node.color)
        return image

    def render_at_depth(self, depth):
        """Renders the image of a given depth/level"""
        image = self._create_image_from_depth(depth)
        image.show()

    def create_gif(self, file_name, duration=1000, loop=0):
        """Creates a gif at the given filename from each level of the tree"""
        images = []
        end_product_image = self._create_image_from_depth(self.max_depth)
        for i in range(self.max_depth):
            image = self._create_image_from_depth(i)
            images.append(image)
        # Add extra final produc images to allow for seeing result longer
        for _ in range(4):
            images.append(end_product_image)
        # Save the images as a gif using Pillow
        images[0].save(
            file_name,
            save_all=True,
            append_images=images[1:],
            duration=duration, loop=loop)
