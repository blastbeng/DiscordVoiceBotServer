import os
import io
from chatterbot.trainers import Trainer
from chatterbot.conversation import Statement
#from google_translate_py import Translator
#from googletrans import Translator
from translate import Translator
from chatterbot import utils
from chatterbot.exceptions import OptionalDependencyImportError


class CustomTrainer(Trainer):

    def train(self):
        from chatterbot.corpus import load_corpus

        data_file_paths = []

        # Get the paths to each file the bot will be trained with
        #for corpus_path in corpus_paths:
        #    data_file_paths.extend(list_corpus_files(corpus_path))


        data_file_paths.append(os.getcwd()+"/data/english/ai.yml")
        data_file_paths.append(os.getcwd()+"/data/english/botprofile.yml")
        data_file_paths.append(os.getcwd()+"/data/english/computers.yml")
        data_file_paths.append(os.getcwd()+"/data/english/conversations.yml")
        data_file_paths.append(os.getcwd()+"/data/english/emotion.yml")
        data_file_paths.append(os.getcwd()+"/data/english/food.yml")
        data_file_paths.append(os.getcwd()+"/data/english/greetings.yml")
        data_file_paths.append(os.getcwd()+"/data/english/health.yml")
        data_file_paths.append(os.getcwd()+"/data/english/humor.yml")
        data_file_paths.append(os.getcwd()+"/data/english/psychology.yml")
        data_file_paths.append(os.getcwd()+"/data/english/science.yml")

        data_file_paths.append(os.getcwd()+"/data/italian/conversations.yml")
        data_file_paths.append(os.getcwd()+"/data/italian/food.yml")
        data_file_paths.append(os.getcwd()+"/data/italian/greetings.yml")
        data_file_paths.append(os.getcwd()+"/data/italian/health.yml")

        translator = Translator(from_lang='en', to_lang="it")

        for corpus, categories, file_path in load_corpus(*data_file_paths):

            statements_to_create = []

            # Train the chat bot with each statement and response pair
            for conversation_count, conversation in enumerate(corpus):

                if self.show_training_progress:
                    utils.print_progress_bar(
                        'Training ' + str(os.path.basename(file_path)),
                        conversation_count + 1,
                        len(corpus)
                    )

                previous_statement_text = None
                previous_statement_search_text = ''

                for text_raw in conversation:

                    if "english" in file_path:
                        text=translator.translate(text_raw)
                    else:
                        text=text_raw

                    statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)

                    statement = Statement(
                        text=text,
                        search_text=statement_search_text,
                        in_response_to=previous_statement_text,
                        search_in_response_to=previous_statement_search_text,
                        conversation='training'
                    )

                    statement.add_tags(*categories)

                    statement = self.get_preprocessed_statement(statement)

                    previous_statement_text = statement.text
                    previous_statement_search_text = statement_search_text

                    statements_to_create.append(statement)

            if statements_to_create:
                self.chatbot.storage.create_many(statements_to_create)
