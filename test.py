import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
import warnings
warnings.filterwarnings("ignore")

class DialoGPTService:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.chat_history_ids = None
        self.load_model()
    
    def load_model(self):
        """Carga el modelo y tokenizer (inferencia o entrenamiento)."""
        print(f"Cargando {self.model_name} en {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Modelo cargado exitosamente.")
    
    def generate_response(self, user_input: str, max_length: int = 1000, num_return_sequences: int = 1):
        """Genera respuesta del bot usando historial de chat."""
        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors='pt')], dim=-1)
        else:
            bot_input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors='pt')
        
        bot_input_ids = bot_input_ids.to(self.device)
        self.chat_history_ids = self.model.generate(
            bot_input_ids,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            temperature=0.7,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True,
            top_k=100,
            top_p=0.95
        )
        
        response = self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        return response
    
    def interactive_chat(self, num_turns: int = 10):
        """Chat interactivo: Usuario y bot alternan turnos."""
        print("¡Chat iniciado! Escribe 'quit' para salir.")
        self.chat_history_ids = None
        for _ in range(num_turns):
            user_input = input("Tú: ")
            if user_input.lower() == 'quit':
                break
            response = self.generate_response(user_input)
            print(f"Bot: {response}")
    
    def prepare_dataset(self, dataset_name="daily_dialog", split="train", max_samples=1000):
        """Prepara dataset para fine-tuning (formato: diálogos concatenados)."""
        dataset = load_dataset(dataset_name, split=split)
        # Toma muestras limitadas para demo rápida
        dataset = dataset.select(range(min(max_samples, len(dataset))))
        
        def format_dialogue(example):
            dialogue = example['dialog']
            # Concatena turnos con EOS tokens para entrenamiento causal
            formatted = tokenizer.eos_token.join(dialogue) + tokenizer.eos_token
            return {'text': formatted}
        
        dataset = dataset.map(format_dialogue)
        return dataset.map(lambda x: self.tokenizer(x['text'], truncation=True, padding=False), batched=True)
    
    def fine_tune(self, dataset, output_dir="./fine_tuned_dialo_gpt", epochs=3, batch_size=4):
        """Fine-tuning con Hugging Face Trainer."""
        print("Iniciando fine-tuning...")
        
        # Tokenizar dataset
        tokenized_dataset = dataset.map(
            lambda examples: self.tokenizer(examples['text'], truncation=True, padding='max_length', max_length=512),
            batched=True,
            remove_columns=dataset.column_names
        )
        tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
        
        # Data collator para language modeling
        data_collator = DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm=False)
        
        # Argumentos de entrenamiento
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            save_steps=500,
            save_total_limit=2,
            prediction_loss_only=True,
            dataloader_pin_memory=False,
            report_to=[]  # Desactiva logging externo
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_dataset
        )
        
        # Entrenar
        trainer.train()
        trainer.save_model(output_dir)
        print(f"Modelo fine-tuneado guardado en {output_dir}")

# Ejemplo de uso
if __name__ == "__main__":
    service = DialoGPTService()
    
    # Opción 1: Solo inferencia (chat interactivo)
    print("=== MODO INFERENCIA ===")
    service.interactive_chat(num_turns=5)
    
    # Opción 2: Fine-tuning (descomenta para ejecutar)
    # print("\n=== MODO ENTRENAMIENTO ===")
    # dataset = service.prepare_dataset("daily_dialog", max_samples=500)
    # service.fine_tune(dataset, epochs=1, batch_size=2)  # Ajusta epochs/batch para tu hardware
    # 
    # # Después de entrenar, usa el modelo fine-tuneado
    # service.model = AutoModelForCausalLM.from_pretrained("./fine_tuned_dialo_gpt")
    # service.load_model()  # Recarga para inferencia
    # service.interactive_chat(num_turns=5)