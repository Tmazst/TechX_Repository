

class users_data:

    def logo(self):
        pass

    def other_docs(self):
        pass

    def website(self):
        pass

    def other_one_page_design(self):
        pass

    def project_data(self,project_title,_dict):
        import json
        self._dict = _dict

        print("Check Type: ",type(project_title),project_title)

        file = project_title.replace(":","_")+".json"

        with open(file,"w") as r_file:

            file = r_file.write(json.dumps(self._dict,indent=4,sort_keys=True))