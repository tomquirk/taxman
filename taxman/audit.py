"""
=================
CSS Audit
Author: Tom Quirk
=================
"""

from bs4 import BeautifulSoup as Bs
import os


class Colour:
    """
    Class for holding ANSI print colours
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Audit(object):
    def __init__(self, basedir):
        self._HTML_file_styles = {} # by file
        self._all_styles = {}   # by style
        self._css_file_styles = {}  # by file
        self._css_all_styles = {}  # by style

        self._BASEDIR = basedir
        if basedir[-1] == '/':
            self._BASEDIR = basedir[:-1]

    def snoopHTML(self, fpath):
        """
        Generates data structure for given file, describing it's HTML elements
        that have and associated style. NOTE: Line numbers are sometimes
        inaccurate.
        :param fpath: str
        :return:
        """
        fname = os.path.basename(fpath)
        self._HTML_file_styles[fpath] = []
        file = open(fpath).read()
        file_lines = file.split('\n')

        soup = Bs(file, 'html.parser')

        tags = soup.find_all()

        for tag in tags:
            styles = {'element': '', 'class': [], 'id': [], 'line_no': 0,
                      'tag': ''}
            if tag.has_attr('class'):
                _class = tag['class']
                styles['class'].append(_class)

            elif tag.has_attr('id'):
                _id = tag['id']
                styles['id'].append(_id)

            # get open tag of element
            styles['element'] = str(tag).strip().split('\n')[0]

            # get tag
            styles['tag'] = tag.name

            # if has style
            if len(styles['class']) != 0 or len(styles['id']) != 0:
                self._HTML_file_styles[fpath].append(styles)

            # clean up classes
            clean_classes = []
            for cgroup in styles['class']:
                for cname in cgroup:
                    clean_classes.append('.' + cname)

            # clean up ids
            clean_ids = []
            for iname in styles['id']:
                clean_ids.append('#' + iname)

            styles['class'] = clean_classes
            styles['id'] = clean_ids

            # get line number in file

            for line in enumerate(file_lines):
                line_no = line[0] + 1
                rline = str(line[1].strip())

                opTag = '<' + styles['tag']

                # check if matched tag on class
                if len(styles['class']) != 0:
                    if opTag in rline and styles['class'][0][1:] in rline:
                        styles['line_no'] = line_no

                # check if matched tag on id
                elif len(styles['id']) != 0:
                    if opTag in rline and styles['id'][0][1:] in rline:
                        styles['line_no'] = line_no

    def snoopHTML_styles(self, fpath):
        """
        Generates data structure organised by class name; each contains
        filename, line number, element and tag.
        :return:
        """
        for tag in self._HTML_file_styles[fpath]:
            for _class in tag['class']:

                struct = {'file': fpath, 'line_no': tag['line_no'],
                          'tag': tag['tag'], 'element': tag['element']}

                # create new style entry
                if _class not in self._all_styles:
                    self._all_styles[_class] = [struct]

                # add to existing style entry
                else:
                    self._all_styles[_class].append(struct)

            for _id in tag['id']:

                struct = {'file': fpath, 'line_no': tag['line_no'],
                          'tag': tag['tag'], 'element': tag['element']}

                # create new style entry
                if _id not in self._all_styles:
                    self._all_styles[_id] = [struct]

                # add to existing style entry
                else:
                    self._all_styles[_id].append(struct)

    def snoopCSS(self, fpath):
        """
        Generates data structure containing style file name, along with its
        associated styles
        :param fpath: str
        :return:
        """
        fname = os.path.basename(fpath)
        self._HTML_file_styles[fpath] = []
        file = open(fpath).read()
        file_lines = file.split('\n')
        class_id = ['.', '&']  # class identifiers for stylus
        id_id = ['#']     # id identifiers for stylus

        struct = {'class': [], 'id': []}

        for line in file_lines:
            line = line.strip()
            if len(line) > 0 and line[0] in class_id \
                    and line not in struct['class']:
                struct['class'].append(line)

            elif len(line) > 0 and line[0] in id_id \
                    and line not in struct['id']:
                struct['id'].append(line)

        self._css_file_styles[fpath] = struct

    def snoopCSS_styles(self, fname):
        """
        Generates key-value pair structure; key = style, value = fname
        :param fname:
        :return:
        """

        for _class in self._css_file_styles[fname]['class']:
            if _class not in self._css_all_styles:
                self._css_all_styles[_class] = fname

        for _id in self._css_file_styles[fname]['id']:
            if _id not in self._css_all_styles:
                self._css_all_styles[_id] = fname

    def diffHTML(self):
        """
        Returns list of dictionaries containing file name, line number and
        element of elements that use undefined style definitions
        :return:
        """
        diff = []
        for style in self._all_styles:
            if style not in self._css_all_styles and '&' + style not in self._css_all_styles and '>' + style not in self._css_all_styles:
                obj = {'style': style, 'location': self._all_styles[style]}
                diff.append(obj)

        return diff

    def diffCSS(self):
        """
        Returns style definitions, with file paths, that are not used in HTML
        :return:
        """
        diff = []
        for style in self._css_all_styles:
            style_and = (style.replace('&.', '.')).replace('>.', '.')
            if style not in self._all_styles and style_and not in self._all_styles:
                obj = {'style': style, 'location': self._css_all_styles[style]}
                diff.append(obj)

        return diff

    def get_HTML_file_styles(self):
        """
        Returns Html file styles struct.
        :return: dict
        """
        return self._HTML_file_styles

    def get_all_styles(self):
        """
        Returns all styles.
        :return: dict
        """
        return self._all_styles

    def crawl(self, cwd):
        """
        Crawls through base directory to generate structs for styles and HTML
        files. Style file extension defaults to '.styl'
        :return:
        """
        cwd += '/'
        os.chdir(cwd)   # change current working dir to 'cwd' arg
        src_files = os.listdir(cwd)
        src_folders = []

        # ignore hidden items
        for item in src_files:
            if item[0] == '.' or item == 'env':     # env, for dev mode
                src_files.remove(item)

        for item in src_files:
            item_path = cwd + item

            if os.path.isfile(item_path):
                if item_path.endswith('.html'):
                    self.snoopHTML(item_path)
                    self.snoopHTML_styles(item_path)

                elif item_path.endswith('.styl'):
                    self.snoopCSS(item_path)
                    self.snoopCSS_styles(item_path)

            else:
                src_folders.append(cwd + item)

        # hardcore recursion
        for folder in src_folders:
            self.crawl(folder)

    def format_results(self, unused_css, undefined_css):
        """
        Prints prettified audit results
        :return:
        """
        overview = '\n\n' + '###############' + Colour.WARNING + '  TAXMAN - CSS AUDIT  ' + Colour.ENDC + "###############\n\n"
        overview += '%d unused CSS styles\n' % len(unused_css)
        overview += '%d undefined CSS styles\n' % len(undefined_css)

        unused_css_formmated = Colour.WARNING + '\nUNUSED CSS STYLES: \n'
        undefined_css_formatted = Colour.WARNING + '\nUNDEFINED CSS STYLES: \n'

        for style in unused_css:
            x = Colour.OKBLUE + '\n' + style['style'] + '\n\t' + Colour.ENDC
            x += Colour.BOLD + 'Filepath: ' + Colour.ENDC + style[
                'location'] + '\n'
            unused_css_formmated += x

        for style in undefined_css:
            x = Colour.OKBLUE + '\n' + style['style'] + '\n' + Colour.ENDC
            for location in style['location']:
                x += '\t' + Colour.BOLD + 'Filepath: ' + Colour.ENDC + location[
                    'file'] + '\n\t'
                x += Colour.BOLD + 'Element: ' + Colour.ENDC + location[
                    'element'] + '\n\t'
                x += Colour.BOLD + 'Line Number: ' + Colour.ENDC + str(
                    location['line_no']) + '\n\n'
            undefined_css_formatted += x

        print(overview)
        print(unused_css_formmated)
        print(undefined_css_formatted)

    def run(self):
        """
        Initial Runner to populate structs
        :return:
        """
        self.crawl(self._BASEDIR)

        unused_css = self.diffCSS()
        undefined_css = self.diffHTML()
        self.format_results(unused_css, undefined_css)