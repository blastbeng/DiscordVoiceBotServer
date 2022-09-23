import os
import io
import random
import logging
from chatterbot.trainers import Trainer
from chatterbot.conversation import Statement
#from google_translate_py import Translator
#from googletrans import Translator
from translate import Translator
from chatterbot import utils
from chatterbot.exceptions import OptionalDependencyImportError


class CustomTrainer(Trainer):

    def __init__(self, chatbot, **kwargs):

        super().__init__(chatbot, **kwargs)

        self.logger = kwargs.get('logger', logging.getLogger(__name__))

        self.translator_email = kwargs.get('translator_email')

        self.translator_provider = kwargs.get('translator_provider')

        self.translator_baseurl = kwargs.get('translator_baseurl')

        if self.translator_email and self.translator_provider == "mymemory":
            self.translator_limit = 50000
        elif self.translator_provider == "mymemory":
            self.translator_limit = 5000
        else:
            self.translator_limit = 0

        self.translator = Translator(from_lang='en', to_lang="it", provider=self.translator_provider, base_url=self.translator_baseurl, email=self.translator_email)


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

        random.shuffle(data_file_paths)

        converted_chars = 0

        for corpus, categories, file_path in load_corpus(*data_file_paths):

            statements_to_create = []

            # Train the chat bot with each statement and response pair
            for conversation_count, conversation in enumerate(corpus):

                if self.translator_limit != 0 and converted_chars >= self.translator_limit and "english" in file_path:
                    break

                if self.show_training_progress:
                    utils.print_progress_bar(
                        'Training ' + str(os.path.basename(file_path)),
                        conversation_count + 1,
                        len(corpus)
                    )

                previous_statement_text = None
                previous_statement_search_text = ''

                for text_raw in conversation:

                    
                    self.logger.info(' Processing "{}"'.format(
                        text_raw
                    ))

                    if "english" in file_path:
                        text=self.translator.translate(text_raw)
                        converted_chars=converted_chars + len(text)
                    else:
                        text=text_raw

                    if "MYMEMORY" not in text:
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


class TranslatedListTrainer(Trainer):
    """
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """

    def __init__(self, chatbot, **kwargs):

        super().__init__(chatbot, **kwargs)

        self.logger = kwargs.get('logger', logging.getLogger(__name__))

        self.translator_email = kwargs.get('translator_email')

        self.translator_provider = kwargs.get('translator_provider')

        self.translator_baseurl = kwargs.get('translator_baseurl')

        if self.translator_email and self.translator_provider == "mymemory":
            self.translator_limit = 50000
        elif self.translator_provider == "mymemory":
            self.translator_limit = 5000
        else:
            self.translator_limit = 0

        self.lang = kwargs.get('lang')

        self.translator = Translator(from_lang=self.lang, to_lang="it", provider=self.translator_provider, base_url=self.translator_baseurl, email=self.translator_email)


    def train(self, conversation):
        """
        Train the chat bot based on the provided list of
        statements that represents a single conversation.
        """
        previous_statement_text = None
        previous_statement_search_text = ''

        statements_to_create = []

        converted_chars = 0

        for conversation_count, text_raw in enumerate(conversation):

            if self.translator_limit != 0 and converted_chars >= self.translator_limit and self.lang == "en":
                break

            if self.show_training_progress:
                utils.print_progress_bar(
                    'Training ' + str(len(conversation)) + ' elements',
                    conversation_count + 1, len(conversation)
                )

            self.logger.info(' Processing "{}"'.format(
                text_raw
            ))

            if self.lang == "en":
                text=self.translator.translate(text_raw)
                converted_chars=converted_chars + len(text)
            else:
                text=text_raw

            if "MYMEMORY" not in text:
                statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)

                statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)

                statement = self.get_preprocessed_statement(
                    Statement(
                        text=text,
                        search_text=statement_search_text,
                        in_response_to=previous_statement_text,
                        search_in_response_to=previous_statement_search_text,
                        conversation='training'
                    )
                )

            previous_statement_text = statement.text
            previous_statement_search_text = statement_search_text

            statements_to_create.append(statement)

        self.chatbot.storage.create_many(statements_to_create)