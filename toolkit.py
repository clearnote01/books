from functools import partial
from pygments.lexers.html import HtmlLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import HTML

style = style_from_pygments_cls(get_style_by_name('monokai'))
text = prompt('Enter HTML: ', lexer=PygmentsLexer(HtmlLexer), style=style,
                      include_default_pygments_style=False)
print('You said: %s' % text)
prompt([('class:red', 'this will be in red')])

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

style = Style.from_dict({
    # User input (default text).
    '':          '#ff0066',

    # Prompt.
    'username': '#884444',
    'at':       '#00aa00',
    'colon':    '#0000aa',
    'pound':    '#00aa00',
    'host':     '#00ffff bg:#444400',
    'path':     'ansicyan underline',
})

message = [
    ('class:username', 'john'),
    ('class:at',       '@'),
    ('class:host',     'localhost'),
    ('class:colon',    ':'),
    ('class:path',     '/user/john'),
    ('class:pound',    '# '),
]
prompt(HTML('<path>this should be in what</path>'), style=style)

text = prompt(message, style=style)
