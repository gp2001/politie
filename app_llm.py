import json
pipeline = """
{
  "melding_content": "md zag 2 automobilisten waren op de vuist",
  "prioriteit": 2,
  "verrijkingen": [
    {
      "type": "persoon",
      "tekst": "2 automobilisten"
    }
  ]
}

{
  "melding_content": "Gaan nu de snelweg op richting Zwolle.",
  "prioriteit": 1,
  "verrijkingen": [
    {
      "type": "locatie",
      "tekst": "snelweg"
    },
    {
      "type": "locatie",
      "tekst": "Zwolle"
    }
  ]
}

{
  "melding_content": "Zijn er collega's in de buurt die even kunnen kijken daar?",
  "prioriteit": 1,
  "verrijkingen": []
}

{
  "melding_content": "Melder heeft nog zicht.",
  "prioriteit": 1,
  "verrijkingen": []
}

{
  "melding_content": "Rijden richten de snelweg nu bij de Wallen.",
  "prioriteit": 1,
  "verrijkingen": [
    {
      "type": "locatie",
      "tekst": "snelweg"
    },
    {
      "type": "locatie",
      "tekst": "Wallen"
    }
  ]
}

{
  "melding_content": "Ze rijden zoekend rond.",
  "prioriteit": 1,
  "verrijkingen": []
}

{
  "melding_content": "Servicemodule: Klantverzoeknummer: 710834701837 Mld belt omdat er een vrouw verdwaald is, WINTER 13-5-1940. Mld heeft gevraagd of ze iemand kunnen bellen voor mevr. De mevr moet naar de PC Hoofdstraat 1 in Amsterdam. Daar woont mevr. Mevr heeft geen geld",
  "prioriteit": 3,
  "verrijkingen": [
    {
      "type": "persoon",
      "tekst": "vrouw"
    },
    {
      "type": "persoon",
      "tekst": "mevr"
    },
    {
      "type": "locatie",
      "tekst": "PC Hoofdstraat 1"
    },
    {
      "type": "locatie",
      "tekst": "Amsterdam"
    }
  ]
}
"""
import transformers
import torch

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
#
# pipeline = transformers.pipeline(
#     "text-generation",
#     model=model_id,
#     model_kwargs={"torch_dtype": torch.bfloat16},
#     device_map="auto",
# )
system = """
Je krijgt meldingen binnen gescheiden door "--------------------------------------------------------------". ik wil dat je per melding een json opstelt en bekijkt of het een prioriteit moet zijn voor de politie. Ook moet je de entiteiten benoemen per bericht in een melding. Doe het zoals:
{
  "melding_content": "Er is een verdachte persoon gezien in de buurt van de supermarkt aan de Hoofdstraat.",
  "prioriteit": 3,
  "verrijkingen": [
    {
      "type": "persoon",
      "tekst": "verdachte persoon"
    },
    {
      "type": "locatie",
      "tekst": "supermarkt aan de Hoofdstraat"
    }
  ]
}
ONLY GIVE JSONS BACK!
"""
prompt = """
18:57

RAZ is deel van kenteken

18:56

-rticn

18:55

geen knt bekend sign ook niet melder zag het met voorbijrijden

18:55

-conf

18:55

waarsch nav aanrijding

18:54

md zag 2 automobilisten waren op de vuist

--------------------------------------------------------------

18:54

Gaan nu de snelweg op richting Zwolle.

18:53

Zijn er collega's in de buurt die even kunnen kijken daar?

18:53

Melder heeft nog zicht.

18:53

Rijden richten de snelweg nu bij de Wallen.

18:53

Ze rijden zoekend rond.

--------------------------------------------------------------
TIC KLAAR

18:57

RTIC ZOEKT

18:12

Servicemodule: Klantverzoeknummer: 710834701837 Mld belt omdat er een vrouw verdwaald is, WINTER 13-5-1940. Mld heeft gevraagd of ze iemand kunnen bellen voor mevr. De mevr moet naar de PC Hoofdstraat 1 in Amsterdam. Daar woont mevr. Mevr heeft geen geld 


"""
# messages = [
#     {"role": "system", "content": system},
#     {"role": "user", "content": txt},
# ]

# prompt = pipeline.tokenizer.apply_chat_template(
#         messages,
#         tokenize=False,
#         add_generation_prompt=True
# )

# terminators = [
#     pipeline.tokenizer.eos_token_id,
#     pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
# ]

# outputs = pipeline(
#     prompt,
#     max_new_tokens=2048,
#     eos_token_id=terminators,
#     do_sample=True,
#     temperature=0.6,
#     top_p=0.9,
# )
# print(outputs[0]["generated_text"][len(prompt):])

print(pipeline)