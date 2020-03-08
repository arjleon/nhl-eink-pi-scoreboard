from PIL import Image, ImageDraw, ImageFont
from enum import Enum, auto
from utils import FontProvider, LogoProvider
import os


class View:

    def draw(self, im: Image, im_ry: Image = None):
        raise NotImplementedError()

    @staticmethod
    def create_canvas(im: Image):
        canvas = ImageDraw.Draw(im)
        return canvas

    @staticmethod
    def xy(box, el, pos):

        x, y = (0, 0)  # Assumed default of View.Pos.start for both x and y

        delta_x = box[0] - el[0]
        delta_y = box[1] - el[1]

        if pos[0] is View.Pos.end:
            x = delta_x
        elif pos[0] is View.Pos.center:
            x = delta_x / 2

        if pos[1] is View.Pos.end:
            y = delta_y
        elif pos[1] is View.Pos.center:
            y = delta_y / 2

        return int(x), int(y)

    class Pos(Enum):
        start = auto()
        center = auto()
        end = auto()


class TextView(View):

    def __init__(self, text: str, font_provider: FontProvider, max_size=20,
                 p=(View.Pos.center, View.Pos.center)):

        self.t = text
        self.fp = font_provider
        self.ms = max_size
        self.p = p

    def get_font(self, s):
        return ImageFont.truetype(self.fp.get_font_path_filename(), s)

    def draw(self, im: Image, im_ry: Image = None):

        canvas = View.create_canvas(im)
        font_size = self.ms
        font = self.get_font(font_size)
        text_size = canvas.textsize(self.t, font)
        while text_size[0] > 8 and text_size[1] > 8 \
                and (text_size[0] > im.size[0] or text_size[1] > im.size[1]):
            font_size -= 2
            font = self.get_font(font_size)
            text_size = canvas.textsize(self.t, font)

        xy = View.xy(im.size, text_size, self.p)
        canvas.multiline_text(xy, self.t, font=font, align='center')


class ImagePathView(View):

    def __init__(self, im_path: str, im_ry_path: str, p=(View.Pos.center, View.Pos.center)):
        self.im_path = im_path
        self.im_ry_path = im_ry_path
        self.p = p

    def draw(self, im: Image, im_ry: Image = None):
        im_b = Image.open(self.im_path)
        new_max_size = (int(min(im.size[0], im_b.size[0])), int(min(im.size[1], im_b.size[1])))
        im_b.thumbnail(new_max_size)
        new_size = im_b.size
        xy = View.xy(im.size, new_size, self.p)
        im.paste(im_b, xy)
        im_b.close()

        if im_ry is not None and os.path.exists(self.im_ry_path):
            im_ry = Image.open(self.im_ry_path)
            im_ry.thumbnail(new_size)
            im_ry.paste(im_ry, xy)
            im_ry.close()


class SpacingLayout(View):

    def __init__(self, spacing_percent, child):
        self.s = spacing_percent
        self.c = child

    def draw(self, im: Image, im_ry: Image = None):
        x_space = int(im.size[0] * self.s)
        y_space = int(im.size[1] * self.s)
        xy = (x_space, y_space)
        new_size = (int(im.size[0] - (x_space * 2)), int(im.size[1] - (y_space * 2)))
        new_image = Image.new('1', new_size, 255)
        new_image_ry = Image.new('1', new_size, 255)
        self.c.draw(new_image, new_image_ry)
        im.paste(new_image, xy)
        if im_ry is not None:
            im_ry.paste(new_image_ry, xy)


class LinearLayout(View):

    def __init__(self, children: [], weights: [int] = None, is_vertical=False):

        if children is None or len(children) == 0:
            raise ValueError('Missing children', children)

        if weights is None:
            weights = [1 for i in range(len(children))]

        if len(children) != len(weights):
            raise ValueError('Mismatch', len(children), len(weights))

        self.children = children
        self.weights = weights
        self.weights_total = 0
        self.is_vertical = is_vertical

        for w in weights:
            self.weights_total += w

    def draw(self, im: Image, im_ry: Image = None):

        x, y = (0, 0)
        w, h = im.size
        for i in range(len(self.children)):
            c = self.children[i]
            percent = self.weights[i] / self.weights_total

            new_w = 0
            new_h = 0
            if self.is_vertical:
                new_h = int(percent * h)
                new_size = (w, new_h)
            else:
                new_w = int(percent * w)
                new_size = (new_w, h)

            new_image = Image.new('1', new_size, 255)
            new_image_ry = Image.new('1', new_size, 255)
            c.draw(new_image, new_image_ry)
            im.paste(new_image, (x, y))
            if im_ry is not None:
                im_ry.paste(new_image_ry, (x, y))
            x += new_w
            y += new_h
            del c, percent, new_w, new_h, new_size, new_image, new_image_ry
