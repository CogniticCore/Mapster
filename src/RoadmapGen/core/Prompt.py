class LlmPrompt:
    def getprompt():
        prompt_template = """Main Topic: {main_topic}
        Current Topic: {current_topic}
        Current Topic Description: {current_description}"""
        return prompt_template