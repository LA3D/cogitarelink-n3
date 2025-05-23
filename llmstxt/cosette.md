<project title="Cosette" summary="Cosette is a Python library that wraps OpenAI's API to provide a higher-level interface for creating AI applications. It automates common patterns while maintaining full control, offering features like stateful chat, image handling, and streamlined tool use.">Things to remember when using Cosette: 

- You must set the `OPENAI_API_KEY` environment variable with your OpenAI API key
- Cosette is designed to work with OpenAI models (e.g. 'o1-preview', 'o1-mini', 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-4-32k', 'gpt-3.5-turbo', 'gpt-3.5-turbo-instruct') and supports multiple providers (OpenAI direct, Azure)
- You can also pass in your own OpenAI client if you wish to change the base URL or other settings.
- Use `Chat()` for maintaining conversation state and handling tool interactions
- When using tools, the library automatically handles the request/response loop
- Image support is built in but only available on compatible models (e.g. not o1 series)<docs><doc title="README" desc="Quick start guide and overview"># cosette



## Install

``` sh
pip install cosette
```

## Getting started

OpenAI’s Python SDK will automatically be installed with Cosette, if you
don’t already have it.

``` python
from cosette import *
```

Cosette only exports the symbols that are needed to use the library, so
you can use `import *` to import them. Alternatively, just use:

``` python
import cosette
```

…and then add the prefix `cosette.` to any usages of the module.

Cosette provides `models`, which is a list of models currently available
from the SDK.

``` python
models
```

    ('gpt-4o',
     'gpt-4-turbo',
     'gpt-4',
     'gpt-4-32k',
     'gpt-3.5-turbo',
     'gpt-3.5-turbo-instruct')

For these examples, we’ll use GPT-4o.

``` python
model = models[0]
```

## Chat

The main interface to Cosette is the
[`Chat`](https://AnswerDotAI.github.io/cosette/core.html#chat) class,
which provides a stateful interface to the models:

``` python
chat = Chat(model, sp="""You are a helpful and concise assistant.""")
chat("I'm Jeremy")
```

Hi Jeremy! How can I assist you today?

<details>

- id: chatcmpl-9R8Z0uRHgWl7XaV6yJtahVDyDTzMZ
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=‘Hi Jeremy! How can I assist you
  today?’, role=‘assistant’, function_call=None, tool_calls=None))\]
- created: 1716254802
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_729ea513f7
- usage: CompletionUsage(completion_tokens=10, prompt_tokens=21,
  total_tokens=31)

</details>

``` python
r = chat("What's my name?")
r
```

Your name is Jeremy. How can I assist you further?

<details>

- id: chatcmpl-9R8Z1c76TFqYFYjyON08CbkAmjerN
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=‘Your name is Jeremy. How can I
  assist you further?’, role=‘assistant’, function_call=None,
  tool_calls=None))\]
- created: 1716254803
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_729ea513f7
- usage: CompletionUsage(completion_tokens=12, prompt_tokens=43,
  total_tokens=55)

</details>

As you see above, displaying the results of a call in a notebook shows
just the message contents, with the other details hidden behind a
collapsible section. Alternatively you can `print` the details:

``` python
print(r)
```

    ChatCompletion(id='chatcmpl-9R8Z1c76TFqYFYjyON08CbkAmjerN', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Your name is Jeremy. How can I assist you further?', role='assistant', function_call=None, tool_calls=None))], created=1716254803, model='gpt-4o-2024-05-13', object='chat.completion', system_fingerprint='fp_729ea513f7', usage=In: 43; Out: 12; Total: 55)

You can use `stream=True` to stream the results as soon as they arrive
(although you will only see the gradual generation if you execute the
notebook yourself, of course!)

``` python
for o in chat("What's your name?", stream=True): print(o, end='')
```

    I don't have a personal name, but you can call me Assistant. How can I help you today, Jeremy?

## Tool use

[Tool use](https://docs.openai.com/claude/docs/tool-use) lets the model
use external tools.

We use [docments](https://fastcore.fast.ai/docments.html) to make
defining Python functions as ergonomic as possible. Each parameter (and
the return value) should have a type, and a docments comment with the
description of what it is. As an example we’ll write a simple function
that adds numbers together, and will tell us when it’s being called:

``` python
def sums(
    a:int,  # First thing to sum
    b:int=1 # Second thing to sum
) -> int: # The sum of the inputs
    "Adds a + b."
    print(f"Finding the sum of {a} and {b}")
    return a + b
```

Sometimes the model will say something like “according to the `sums`
tool the answer is” – generally we’d rather it just tells the user the
answer, so we can use a system prompt to help with this:

``` python
sp = "Never mention what tools you use."
```

We’ll get the model to add up some long numbers:

``` python
a,b = 604542,6458932
pr = f"What is {a}+{b}?"
pr
```

    'What is 604542+6458932?'

To use tools, pass a list of them to
[`Chat`](https://AnswerDotAI.github.io/cosette/core.html#chat):

``` python
chat = Chat(model, sp=sp, tools=[sums])
```

Now when we call that with our prompt, the model doesn’t return the
answer, but instead returns a `tool_use` message, which means we have to
call the named tool with the provided parameters:

``` python
r = chat(pr)
r
```

    Finding the sum of 604542 and 6458932

- id: chatcmpl-9R8Z2JNenseQyQoseIs8XNImmy2Bo
- choices: \[Choice(finish_reason=‘tool_calls’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=None, role=‘assistant’,
  function_call=None,
  tool_calls=\[ChatCompletionMessageToolCall(id=‘call_HV4yaZEY1OYK1zYouAcVwfZK’,
  function=Function(arguments=‘{“a”:604542,“b”:6458932}’, name=‘sums’),
  type=‘function’)\]))\]
- created: 1716254804
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_729ea513f7
- usage: CompletionUsage(completion_tokens=21, prompt_tokens=96,
  total_tokens=117)

Cosette handles all that for us – we just have to pass along the
message, and it all happens automatically:

``` python
chat()
```

The sum of 604542 and 6458932 is 7063474.

<details>

- id: chatcmpl-9R8Z4CrFU3zd71acZzdCsQFQDHxp9
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=‘The sum of 604542 and 6458932
  is 7063474.’, role=‘assistant’, function_call=None,
  tool_calls=None))\]
- created: 1716254806
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_729ea513f7
- usage: CompletionUsage(completion_tokens=18, prompt_tokens=128,
  total_tokens=146)

</details>

You can see how many tokens have been used at any time by checking the
`use` property.

``` python
chat.use
```

    In: 224; Out: 39; Total: 263

### Tool loop

We can do everything needed to use tools in a single step, by using
[`Chat.toolloop`](https://AnswerDotAI.github.io/cosette/toolloop.html#chat.toolloop).
This can even call multiple tools as needed solve a problem. For
example, let’s define a tool to handle multiplication:

``` python
def mults(
    a:int,  # First thing to multiply
    b:int=1 # Second thing to multiply
) -> int: # The product of the inputs
    "Multiplies a * b."
    print(f"Finding the product of {a} and {b}")
    return a * b
```

Now with a single call we can calculate `(a+b)*2` – by passing
`show_trace` we can see each response from the model in the process:

``` python
chat = Chat(model, sp=sp, tools=[sums,mults])
pr = f'Calculate ({a}+{b})*2'
pr
```

    'Calculate (604542+6458932)*2'

``` python
def pchoice(r): print(r.choices[0])
```

``` python
r = chat.toolloop(pr, trace_func=pchoice)
```

    Finding the sum of 604542 and 6458932
    Finding the product of 2 and 1
    Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_OfypQBQoAuIUksucevaxwH5Z', function=Function(arguments='{"a": 604542, "b": 6458932}', name='sums'), type='function'), ChatCompletionMessageToolCall(id='call_yKAL5o96cDef83OFJhDB21MM', function=Function(arguments='{"a": 2}', name='mults'), type='function')]))
    Finding the product of 7063474 and 2
    Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_Ffye7Tf65CjVjwwx8Sp8031i', function=Function(arguments='{"a":7063474,"b":2}', name='mults'), type='function')]))
    Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='The result of \\((604542 + 6458932) \\times 2\\) is 14,126,948.', role='assistant', function_call=None, tool_calls=None))

OpenAI uses special tags for math equations, which we can replace using
[`wrap_latex`](https://AnswerDotAI.github.io/cosette/core.html#wrap_latex):

``` python
wrap_latex(contents(r))
```

The result of $(604542 + 6458932) \times 2$ is 14,126,948.

## Images

As everyone knows, when testing image APIs you have to use a cute puppy.

``` python
fn = Path('samples/puppy.jpg')
display.Image(filename=fn, width=200)
```

<img src="index_files/figure-commonmark/cell-21-output-1.jpeg"
width="200" />

We create a
[`Chat`](https://AnswerDotAI.github.io/cosette/core.html#chat) object as
before:

``` python
chat = Chat(model)
```

Claudia expects images as a list of bytes, so we read in the file:

``` python
img = fn.read_bytes()
```

Prompts to Claudia can be lists, containing text, images, or both, eg:

``` python
chat([img, "In brief, what color flowers are in this image?"])
```

The flowers in the image are purple.

<details>

- id: chatcmpl-9R8Vqpx62OezZDjAt3SIfnjMpH3I8
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=‘The flowers in the image are
  purple.’, role=‘assistant’, function_call=None, tool_calls=None))\]
- created: 1716254606
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_927397958d
- usage: CompletionUsage(completion_tokens=8, prompt_tokens=273,
  total_tokens=281)

</details>

The image is included as input tokens.

``` python
chat.use
```

    In: 273; Out: 8; Total: 281

Alternatively, Cosette supports creating a multi-stage chat with
separate image and text prompts. For instance, you can pass just the
image as the initial prompt (in which case the model will make some
general comments about what it sees), and then follow up with questions
in additional prompts:

``` python
chat = Chat(model)
chat(img)
```

What an adorable puppy! This puppy has a white and light brown coat and
is lying on green grass next to some purple flowers. Puppies like this
are commonly seen from breeds such as Cavalier King Charles Spaniels,
though without more context, it’s difficult to identify the breed
precisely. It looks very playful and cute!

<details>

- id: chatcmpl-9R8VsAnTWr9k1DShC7mZsnhRtqxRA
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=“What an adorable puppy! This
  puppy has a white and light brown coat and is lying on green grass
  next to some purple flowers. Puppies like this are commonly seen from
  breeds such as Cavalier King Charles Spaniels, though without more
  context, it’s difficult to identify the breed precisely. It looks very
  playful and cute!”, role=‘assistant’, function_call=None,
  tool_calls=None))\]
- created: 1716254608
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_927397958d
- usage: CompletionUsage(completion_tokens=63, prompt_tokens=262,
  total_tokens=325)

</details>

``` python
chat('What direction is the puppy facing?')
```

The puppy is facing slightly to the right of the camera, with its head
turned towards the viewer. Its body is positioned in such a way that
suggests it is laying down or resting on the grass.

<details>

- id: chatcmpl-9R8VuzGIABwg341oOHMXbGGa7daya
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=‘The puppy is facing slightly to
  the right of the camera, with its head turned towards the viewer. Its
  body is positioned in such a way that suggests it is laying down or
  resting on the grass.’, role=‘assistant’, function_call=None,
  tool_calls=None))\]
- created: 1716254610
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_927397958d
- usage: CompletionUsage(completion_tokens=40, prompt_tokens=340,
  total_tokens=380)

</details>

``` python
chat('What color is it?')
```

The puppy has a predominantly white coat with light brown patches,
particularly around its ears and eyes. This coloration is commonly seen
in certain breeds, such as the Cavalier King Charles Spaniel.

<details>

- id: chatcmpl-9R8Vwtlu6aDEGQ8O7bZFk8rfT9FGL
- choices: \[Choice(finish_reason=‘stop’, index=0, logprobs=None,
  message=ChatCompletionMessage(content=‘The puppy has a predominantly
  white coat with light brown patches, particularly around its ears and
  eyes. This coloration is commonly seen in certain breeds, such as the
  Cavalier King Charles Spaniel.’, role=‘assistant’, function_call=None,
  tool_calls=None))\]
- created: 1716254612
- model: gpt-4o-2024-05-13
- object: chat.completion
- system_fingerprint: fp_927397958d
- usage: CompletionUsage(completion_tokens=38, prompt_tokens=393,
  total_tokens=431)

</details>

Note that the image is passed in again for every input in the dialog, so
that number of input tokens increases quickly with this kind of chat.

``` python
chat.use
```

    In: 995; Out: 141; Total: 1136</doc></docs><api><doc title="API List" desc="A succint list of all functions and methods in cosette."># cosette Module Documentation

## cosette.core

- `def find_block(r)`
    Find the message in `r`.

- `def contents(r)`
    Helper to get the contents from response `r`.

- `def usage(inp, out)`
    Slightly more concise version of `CompletionUsage`.

- `@patch def __add__(self, b)`
    Add together each of `input_tokens` and `output_tokens`

- `def wrap_latex(text, md)`
    Replace OpenAI LaTeX codes with markdown-compatible ones

- `class Client`
    - `def __init__(self, model, cli)`
        Basic LLM messages client.


- `@patch @delegates(Completions.create) def __call__(self, msgs, sp, maxtok, stream, **kwargs)`
    Make a call to LLM.

- `def mk_toolres(r, ns, obj)`
    Create a `tool_result` message from response `r`.

- `@patch @delegates(Client.__call__) def structured(self, msgs, tools, obj, ns, **kwargs)`
    Return the value of all tool calls (generally used for structured outputs)

- `class Chat`
    - `def __init__(self, model, cli, sp, tools, tool_choice)`
        OpenAI chat client.

    - `@property def use`

## cosette.toolloop

- `@patch @delegates(Completions.create) def toolloop(self, pr, max_steps, trace_func, cont_func, **kwargs)`
    Add prompt `pr` to dialog and get a response from the model, automatically following up with `tool_use` messages
</doc></api></project>