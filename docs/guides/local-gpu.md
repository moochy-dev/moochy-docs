# Donate from your own GPU

If you run a model on your own hardware, you can donate tokens from it instead of from a paid API key. The Moochy app sends each request to your local server, exactly as it would to a provider, and returns the answer encrypted. It costs you electricity, not API credit.

Supported servers (anything that speaks the OpenAI chat format works the same way):

| Server | Default address | Parallel requests |
|---|---|---|
| **Ollama** | `http://127.0.0.1:11434` | `OLLAMA_NUM_PARALLEL` |
| **LM Studio** | `http://127.0.0.1:1234` | set in the server settings |
| **vLLM** | `http://127.0.0.1:8000` | `--max-num-seqs` |
| **llama.cpp** (`llama-server`) | `http://127.0.0.1:8080` | `-np` |

Everything in the [donor guide](donor.md) still applies: the app runs no commands, locks itself down, checks every request, and keeps its own limits. This page covers what is different.

---

## 1. Start your server

Examples; use the model you want to donate.

```sh
OLLAMA_NUM_PARALLEL=4 ollama serve                       # then: ollama pull qwen2.5:7b
llama-server -m qwen2.5-7b-instruct-q4_k_m.gguf --port 8080 -np 4
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000 --max-num-seqs 4
```

In LM Studio, load a model and start the local server from the Developer tab.

## 2. Add it to Moochy

```sh
moochy keys add local --base-url http://127.0.0.1:11434 \
  --model local/qwen2.5-7b-q4=qwen2.5:7b
```

- `--base-url` is your server's address only (no path). Moochy calls `<base>/v1/chat/completions`.
- `--model local/<public id>=<server id>` maps a public model id to the name your server uses. Repeat `--model` for each model. If you leave it out, the command lists the models your server offers so you can pick. The public id must start with `local/`: a quantised model on your machine is not the same as the hosted model, so projects choose it explicitly. Use an id from the list of local models Moochy knows (shown on moochy.dev and by `GET /v1/models` for projects that accept local donations).
- An API key is optional. Ollama and LM Studio ignore keys; vLLM uses one only if you started it with `--api-key`. If yours needs one, add `--key-stdin` and pipe it in, as for a provider key.

Then match the number of requests Moochy sends at once to what your server can run in parallel:

```sh
moochy config set slots_max 4
```

Donate as usual: **Donate tokens** on the project's page, or `moochy donate --repo owner/name --cap '$10'`. A local donation serves only the `local/…` models you added.

## 3. Which addresses are allowed

The app only talks to servers you control on your own machine or network:

| Address | Result |
|---|---|
| Loopback (`127.0.0.1`, `::1`) | Accepted |
| Your local network (`10.x`, `172.16–31.x`, `192.168.x`, IPv6 ULA, Tailscale-style `100.64.x`) | Accepted, with a note that requests cross your network, in clear text if you use `http://` |
| Link-local addresses, including cloud metadata (`169.254.x`, `fe80::`), and multicast or broadcast | Always refused |
| Public addresses and host names | Refused: a name can be re-pointed elsewhere later. A development flag exists only for testing the app |

## 4. What is checked

- **Cloud models are refused.** Some servers can forward a model to a cloud service billed to your account (for example Ollama models tagged `cloud`). Moochy refuses those, so a "local" donation never spends your money elsewhere.
- **The same safety checks as hosted providers**, plus a refusal of server-specific options (sampling extras, template overrides, server options). Only the model name and the request for usage numbers are changed before the call.
- **Longer waits.** A local server may need time to load the model and read a long prompt, so Moochy waits up to 5 minutes for the first byte.
- **Responses** go through the same checks on the maintainer's side as any donor's: rebuilt event by event, tool calls checked, signed, and released only to sandboxed agents.

## 5. Self-reported usage

With a hosted provider, the provider counts tokens and bills you, so usage is backed by a bill. On your own GPU nobody bills anyone, and the token counts come from your own server. Moochy cannot check them. So local donations are treated as a separate, lower-trust kind of donation:

- token counts are labelled **self-reported** wherever they appear;
- they count toward a project's goal in **tokens**, and toward a separate local leaderboard, never toward dollar totals or the money leaderboard;
- receipts settle at $0, and your limits in dollars (monthly, weekly, daily) are not used;
- the maintainer's app still checks each receipt against what it received (visible output within ±25%) and files a signed dispute when it does not match.

Where the server reports usage (forced on for every request), Moochy uses it. llama.cpp's timing counters give exact numbers too; otherwise usage is estimated from the streamed output and marked as estimated.

## 6. Things to know

- Projects see your model as `local/…`, never as the hosted model it was derived from, and use it only when they ask for that model.
- Your server sees the prompts it serves, like any donor's provider. Keep it on your machine or a network you trust.
- Answers from small or heavily quantised models can be weak. Offer models you would use yourself.
