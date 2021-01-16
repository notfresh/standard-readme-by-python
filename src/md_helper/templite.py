"""A simple Python template renderer, for a nano-subset of Django syntax."""

# Coincidentally named the same as http://code.activestate.com/recipes/496702/

import re
import os

class TempliteSyntaxError(ValueError):
    """Raised when a template has a syntax error."""
    pass


class CodeBuilder(object):
    """Build source code conveniently."""

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def __str__(self):
        return "".join(str(c) for c in self.code)

    def add_line(self, line):
        """Add a line of source to the code.

        Indentation and newline will be added for you, don't provide them.

        """
        self.code.extend([" " * self.indent_level, line, "\n"])

    def add_section(self):
        """Add a section, a sub-CodeBuilder."""
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    INDENT_STEP = 4      # PEP8 says so!

    def indent(self):
        """Increase the current indent for following lines."""
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """Decrease the current indent for following lines."""
        self.indent_level -= self.INDENT_STEP

    def get_globals(self):
        """Execute the code, and return a dict of globals it defines."""
        # A check that the caller really finished all the blocks they started.
        assert self.indent_level == 0
        # Get the Python source as a single string.
        python_source = str(self)
        # Execute the source, defining globals, and return them.
        global_namespace = {} # return a dict
        exec(python_source, global_namespace)
        return global_namespace


class Templite(object): # @templite @模板引擎
    """A simple template renderer, for a nano-subset of Django syntax.

    Supported constructs are extended variable access::

        {{var.modifer.modifier|filter|filter}}

    loops::

        {% for var in list %}...{% endfor %}

    and ifs::

        {% if var %}...{% endif %}

    Comments are within curly-hash markers::

        {# This will be ignored #}

    Construct a Templite with the template text, then use `render` against a
    dictionary context to create a finished string::

        templite = Templite('''
            <h1>Hello {{name|upper}}!</h1>
            {% for topic in topics %}
                <p>You are interested in {{topic}}.</p>
            {% endif %}
            ''',
            {'upper': str.upper},
        )
        text = templite.render({
            'name': "Ned",
            'topics': ['Python', 'Geometry', 'Juggling'],
        })

    """
    def __init__(self, text, *contexts):
        self.save_path = 'standard.md'
        """Construct a Templite with the given `text`.

        `contexts` are dictionaries of values to use for future renderings.
        These are good for filters and global values.

        """
        template = text
        template_path = ''
        cwd = os.getcwd()
        if os.path.exists(template):
            template_path = template
        elif os.path.exists(os.path.join(cwd, template)):
            template_path = os.path.join(cwd, template)
        else:
            pass

        if template_path:
            with open(template_path, encoding='utf-8') as file:
                template = file.read()
        text = template

        self.context = {}
        for context in contexts:
            self.context.update(context)

        self.all_vars = set()
        self.loop_vars = set()

        # We construct a function in source form, then compile it and hold onto
        # it, and execute it to render the template.
        code = CodeBuilder()

        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")

        buffered = [] # @test1, annoate to line 195

        def flush_output():
            """Force `buffered` to the code builder."""
            if len(buffered) == 1:
                code.add_line("append_result(%s)" % buffered[0])
            elif len(buffered) > 1:
                code.add_line("extend_result([%s])" % ", ".join(buffered))
            del buffered[:]

        ops_stack = [] # this is a control flow stack only.

        # Split the text to form a list of tokens.

        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text) # text is passed from the entrance, the full template text
        def lstrip(x): #
            if re.match("^\s+$",x): # 只有换行符和空格
                return x
            else:
                return x.lstrip()
        # tokens = [lstrip(item) for item in tokens]
        for token in tokens:
            if token.startswith('{#'):
                # Comment: ignore it and move on.
                continue
            elif token.startswith('{{'): # {{ variable }}
                # An expression to evaluate.
                expr = self._expr_code(token[2:-2].strip()) # so, here, we format the placeholder with  the injected varibles
                buffered.append("to_str(%s)" % expr)
            elif token.startswith('{%'): #
                # Action tag: split into words and parse further.there must be an incursion
                flush_output() # {% is a control flow, so flush the buffer
                words = token[2:-2].strip().split()
                if words[0] == 'if':
                    # An if statement: evaluate the expression to determine if.
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    ops_stack.append('if')
                    code.add_line("if %s:" % self._expr_code(words[1])) # Meet if, indent
                    code.indent()
                elif words[0] == 'for': # remember, startwith for, it's a seperated line.
                    # A loop: iterate over expression result.
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars) # here, is a little hard, skip if first
                    code.add_line(
                        "for c_%s in %s:" % (
                            words[1],
                            self._expr_code(words[3])
                        )
                    )
                    code.indent()
                elif words[0].startswith('end'): # endif or endfor
                    # Endsomething.  Pop the ops stack.
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack: # the control stack is empty, no match starting symbol
                        self._syntax_error("Too many ends", token)
                    start_what = ops_stack.pop()
                    if start_what != end_what: # pop and match
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
                else: # so the control flow symbols are limited to: if, for, end
                    self._syntax_error("Don't understand tag", words[0])
            else: # last if at line 144
                # Literal content.  If it isn't empty, output it.
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            self._syntax_error("Unmatched action tag", ops_stack[-1])

        flush_output()
        # vars_code is a code block at the beginning of the to-compile render function, so vars_code is a placeholder
        for var_name in self.all_vars - self.loop_vars: # L160 add the loop_vars, in _expr_code, add the all_vars
            vars_code.add_line("c_%s = context.get(%r, '')" % (var_name, var_name)) # @support the missing value
        code.add_line("return ''.join(result)")
        code.dedent()
        self._render_function = code.get_globals()['render_function']

    def _expr_code(self, expr):
        """Generate a Python expression for `expr`."""
        if "|" in expr:
            pipes = expr.split("|")
            code = self._expr_code(pipes[0]) # recurse
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code) # here, we can see, we take the old code as the new function parameter
        elif "." in expr:  # example: a.name.first
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ", ".join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code

    def _syntax_error(self, msg, thing):
        """Raise a syntax error using `msg`, and showing `thing`."""
        raise TempliteSyntaxError("%s: %r" % (msg, thing))

    def _variable(self, name, vars_set):
        """Track that `name` is used as a variable.

        Adds the name to `vars_set`, a set of variable names.

        Raises an syntax error if `name` is not a valid name.

        """
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    def save_file(self, txt, output_path):
        # output_path = output_path or self.save_path
        print('@output path')
        print(output_path)
        with open(output_path, 'w+') as f:
            f.write(txt)

    def render(self, context=None, output_path=None):
        """Render this template by applying it to `context`.
        `context` is a dictionary of values to use in this rendering.
        """
        # Make the complete context we'll use. the context is the variables we want to update..
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        txt = self._render_function(render_context, self._do_dots)
        self.save_file(txt, output_path=output_path)
        print('@txt')
        print(txt)# @txt
        return txt

    def _do_dots(self, value, *dots):
        """Evaluate dotted expressions at runtime."""
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value.get(dot, '')
            if callable(value): #如果是一个可调用的函数或者对象的话!
                value = value()
        return value

