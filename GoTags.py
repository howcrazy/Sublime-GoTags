from datetime import datetime
import re

import sublime
import sublime_plugin

def debug(msg):
    if load_setting('debug', False):
        print('[%s]GoTags Debug: %s' % (now(), msg))


def error(msg):
    msg = 'GoTags Error: %s' % msg
    print('[%s]%s' % (now(), msg))
    key = 'GoTags'
    view = sublime.active_window().active_view()
    view.set_status(key, msg)
    sublime.set_timeout(lambda: view.erase_status(key), 3000)


def now():
    return datetime.now().strftime('%H:%M:%S')


def load_setting(key, default=None, filename='GoTags.sublime-settings'):
    key = key.strip()
    if not key:
        return default
    settings = sublime.load_settings('GoTags.sublime-settings')
    keys = [k.strip() for k in key.split('.')]
    keys, key = keys[: -1], keys[-1: ][0]
    setting = settings
    for k in keys:
        if not (k in setting if isinstance(setting, dict) else setting.has(k)):
            return default
        setting = setting.get(k)
    return setting.get(key, default)


def snake_cased_name(name):
    offset = ord('a') - ord('A')
    def t(matchObj):
        g = matchObj.group(0)
        c = chr(ord(g) + offset)
        if matchObj.start(0) > 0:
            return "_%s" % c
        return c
    return re.sub(r'[A-Z]', t, name)


class JsonTag(object):
    @classmethod
    def add_tag(cls, name, typ, tags, **kwargs):
        name = snake_cased_name(name)
        if tags == '':
            return 'json:"%s"' % name
        prog = re.compile(r'(?s)json:".*?"')
        m = prog.search(tags)
        if not m:
            return ' '.join([tags, 'json:"%s"' % name])
        return tags

    @classmethod
    def remove_tag(cls, name, typ, tags, **kwargs):
        if tags == '':
            return ''
        prog = re.compile(r'(?s)[\t ]*json:".*?"')
        m = prog.search(tags)
        if not m:
            return tags
        return prog.sub('', tags)


class XmlTag(object):
    @classmethod
    def add_tag(cls, name, typ, tags, **kwargs):
        name = snake_cased_name(name)
        if tags == '':
            return 'xml:"%s"' % name
        prog = re.compile(r'(?s)xml:".*?"')
        m = prog.search(tags)
        if not m:
            return ' '.join([tags, 'xml:"%s"' % name])
        return tags

    @classmethod
    def remove_tag(cls, name, typ, tags, **kwargs):
        if tags == '':
            return ''
        prog = re.compile(r'(?s)[\t ]*xml:".*?"')
        m = prog.search(tags)
        if not m:
            return tags
        return prog.sub('', tags)


class XormTag(object):
    @classmethod
    def add_tag(cls, name, typ, tags, **kwargs):
        if tags == '':
            return 'xorm:"%s"' % get_xorm_type(typ)
        prog = re.compile(r'(?s)xorm:".*?"')
        m = prog.search(tags)
        if not m:
            return ' '.join([tags, 'xorm:"%s"' % get_xorm_type(typ)])
        return tags

    @classmethod
    def remove_tag(cls, name, typ, tags, **kwargs):
        if tags == '':
            return ''
        prog = re.compile(r'(?s)[\t ]*xorm:".*?"')
        m = prog.search(tags)
        if not m:
            return tags
        return prog.sub('', tags)


ACTION_INSERT_JSON = 'JSON: Append tags'
ACTION_INSERT_XML = 'Xml: Append tags'
ACTION_INSERT_XORM = 'Xorm: Append tags'
ACTION_REMOVE_JSON = 'JSON: Remove tags all'
ACTION_REMOVE_XML = 'Xml: Remove tags all'
ACTION_REMOVE_XORM = 'Xorm: Remove tags all'
ACTIONS = [
    (ACTION_INSERT_JSON, JsonTag.add_tag),
    (ACTION_INSERT_XML, XmlTag.add_tag),
    (ACTION_INSERT_XORM, XormTag.add_tag),
    (ACTION_REMOVE_JSON, JsonTag.remove_tag),
    (ACTION_REMOVE_XML, XmlTag.remove_tag),
    (ACTION_REMOVE_XORM, XormTag.remove_tag),
]


class Member(object):
    def __init__(self, textCommand, region):
        super(Member, self).__init__()

        self.cmd = textCommand
        self.region = region
        self.orig_context = self.cmd.view.substr(self.region)
        debug(self.orig_context)

    def parse(self, tag_type):
        return re.sub(
            r'(?s)^[\t ]*(?P<name>[\w_]+)[\t ]+(?P<typ>(interface\{\}|[\w._\[\]]+))([\t ]+`(?P<tags>.*?)`)?',
            lambda matchObj: self._parse(matchObj, tag_type),
            self.orig_context,
        )

    def _parse(self, matchObj, tag_type):
        d = matchObj.groupdict()
        d['tags'] = (d['tags'] or '').strip()
        if tag_type < len(ACTIONS):
            type_name, action = ACTIONS[tag_type]
            d['tags'] = action(**d)
        return '\t%(name)s\t%(typ)s\t`%(tags)s`' % (d)


class GoTagsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not (self.view.file_name() or '').endswith('.go'):
            error('GoTags works only in .go file')
            return
        self.view.window().show_quick_panel([ac[0] for ac in ACTIONS], lambda i: i > -1 and self.view.run_command('go_typ_tags', dict(typ=i)))


class GoTypTagsCommand(sublime_plugin.TextCommand):
    def run(self, edit, typ):
        self.line_endings = self.view.line_endings()
        self.linesep = '\n' if self.line_endings == 'Unix' else '\r\n' if self.line_endings == 'Windows' else '\r'
        debug('LINE_ENDINGS: %s' % self.line_endings)
        debug('LINESEP: %s' % repr(self.linesep))

        sels = self.view.sel()
        if not len(sels):
            return

        regions = []
        for sel in sels:
            begin = a = self.view.line(sel.begin()).begin()
            b = self.view.line(sel.end()).end()
            while begin < b:
                try:
                    r = self.get_struct_context(begin, b)
                    begin = r.end() + 1
                except Exception as e:
                    error(str(e))
                    break
                regions.append(r)

        if len(regions) < 1:
            debug('nothing to do')
            return
        self.go_tags(edit, typ, regions)

    def go_tags(self, edit, tag_type, regions):
        find = self.view.find
        r_offset = 0
        for region in regions:
            debug(self.view.substr(region))
            begin = skip = region.begin() + r_offset
            max_end = region.end() + r_offset
            i = 1000
            while begin < max_end:
                i -= 1
                if i < 0:
                    break
                line = self.view.line(begin)
                if begin < skip:
                    begin = line.end() + 1
                    continue
                r = find(r'(?s)^[\t ]*[\w_]+[\t ]+(interface\{\}|[\w._\[\]]+)([\t ]+`.*?`)?', max(skip, begin))
                if r.empty():
                    break
                if r.begin() < line.end():
                    t = self.view.size()
                    self.view.replace(edit, r, Member(self, r).parse(tag_type))
                    offset = self.view.size() - t
                    begin = r.end() + 1 + offset
                    skip += offset
                    max_end += offset
                    r_offset += offset
                    continue
                r = find(r'.*?(`.*?`|//)*?/\*', r.end()+1 if r.end() < line.end() else line.begin())
                if r.empty() or r.begin() > line.end():
                    begin = line.end() + 1
                    continue
                r = find(r'\*/', r.end()+1)
                if r.empty():
                    break
                skip = r.end()
                begin = r.end() + 1

    def get_struct_context(self, begin, b):
        r = self.view.find(
            r'^[\t ]*type [\w]+ +struct +\{', begin)
        if r.begin() < 0 or r.begin() > b:
            debug('find region %s in region %s' % (r, (begin, b)))
            raise Exception('struct unfound!')
        end = r.end()
        max = self.view.size()
        while end < max:
            c = self.view.substr(end)
            if c == '/' and self.view.substr(end+1) == '*':
                m = self.view.find(r'\*/', end+2)
                c = '/*'
            elif c == '`':
                m = self.view.find(r'`', end+1)
            elif c in ['"', "'"]:
                m = self.view.find(r'.*?([^\\]|\\\\)%s'%c, end+1)
            elif c == '/' and self.view.substr(end+1) == '/':
                m = self.view.find(self.linesep, end+2)
                c = '//'
            elif c == '{':
                m = self.view.find(r'(?s)([^\}]*?\{.*?\}){0,}.*?\}', end+1)
            elif c == '}':
                break
            else:
                end += 1
                continue
            if not m:
                raise Exception('unfound ending of "%s"' % c)
            end = m.end()
        else:
            end = 0
        if end < 1:
            raise Exception('not match')
        return sublime.Region(r.end()+len(self.linesep), end-1)


XORM_TYPES = None

def get_xorm_type(typ):
    global XORM_TYPES
    if XORM_TYPES is None:
        ts = load_setting('xorm.types', {})
        xts = {}
        for gts, xt in ts.items():
            for gt in gts.strip().split(','):
                gt = gt.strip()
                if gt:
                    xts[gt] = xt
        XORM_TYPES = xts
    return XORM_TYPES.get(typ, '')
