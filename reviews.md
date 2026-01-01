Replication of the Auditing Game Model Organism
https://arxiv.org/abs/2511.01689
Abhay Sheshadri, Rohan Gupta, Kei Nishimura-Gasparian et al. Anthropic Blog·2025
Rating: 4.0/5

Value for the community (generally very excited about auditing game benchmarks) 

Valuable new scientific contributions too: in particular, that adversarial training against profile attacks (and other inputs) generalizes to robustness against user persona and “base model” sampling. 

This generalization is interesting, though I’m curious whether profile robustness could be induced without directly training against it (by e.g. training on synthetic documents with information about profile attacks)

============================================================

Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI
https://arxiv.org/pdf/2511.01689.pdf
Sharan Maiya, Henning Bartsch, Nathan Lambert et al. arXiv·2025
Rating: 4.0/5

Great to see academic / open work on character training. 

While not the focus of the paper, was pretty interested in the DPO expert distillation pipeline (with a stronger model + spec generating positive examples and base model generating negative examples). Curious how this compares to on-policy distillation https://thinkingmachines.ai/blog/on-policy-distillation/. 

They test robustness to “profiles” of default assistant personas, but I’d be curious to see if introspection training improves peril robustness in general. Intuitively, having a more salient notion of “being” the assistant with particular values would improve robustness to e.g. harmfulness prefills, though afaik this hasn’t been tested empirically (and Claude models are still susceptible to prefills, so clearly this effect isn’t massive)
