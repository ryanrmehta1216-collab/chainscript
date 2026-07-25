import os
import json

# 1. Target the exact VS Code extensions folder on your Windows machine
ext_dir = os.path.expanduser(r"~\.vscode\extensions\chainscript-language")
syntaxes_dir = os.path.join(ext_dir, "syntaxes")

# 2. Create the folders automatically
os.makedirs(syntaxes_dir, exist_ok=True)

# 3. Define the extension manifest
package_json = {
  "name": "chainscript",
  "displayName": "ChainScript Language Support",
  "description": "Syntax highlighting for the ChainScript AI orchestration language.",
  "version": "1.0.0",
  "publisher": "ChainScriptPro",
  "engines": { "vscode": "^1.60.0" },
  "categories": ["Programming Languages"],
  "contributes": {
    "languages": [{
        "id": "chainscript",
        "aliases": ["ChainScript", "chain"],
        "extensions": [".chain"]
    }],
    "grammars": [{
        "language": "chainscript",
        "scopeName": "source.chain",
        "path": "./syntaxes/chainscript.tmLanguage.json"
    }]
  }
}

# 4. Define the syntax highlighting rules
grammar_json = {
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "ChainScript",
  "scopeName": "source.chain",
  "patterns": [
    {"include": "#comments"},
    {"include": "#strings"},
    {"include": "#keywords"},
    {"include": "#numbers"}
  ],
  "repository": {
    "comments": {
      "patterns": [{"name": "comment.line.double-slash.chainscript", "match": "//.*$"}]
    },
    "strings": {
      "name": "string.quoted.double.chainscript",
      "begin": "\"", "end": "\"",
      "patterns": [{"name": "constant.character.escape.chainscript", "match": "\\\\."}]
    },
    "keywords": {
      "patterns": [
        {"name": "keyword.control.chainscript", "match": "\\b(IF|THEN|ELSE|ENDIF|WHILE|DO|ENDWHILE|TRY|CATCH|RETURN)\\b"},
        {"name": "keyword.other.chainscript", "match": "\\b(AGENT|MODEL|ROLE|TEMPERATURE|SET|INVOKE|WITH|USING|MEMORY|AS|JUDGE|FUNCTION|WRITE|READ|RUN_SHELL)\\b"},
        {"name": "keyword.operator.chainscript", "match": "\\b(CONTAINS)\\b|==|!=|\\+|=|:"}
      ]
    },
    "numbers": {
      "name": "constant.numeric.chainscript", "match": "\\b\\d+(\\.\\d+)?\\b"
    }
  }
}

# 5. Write the files to the system
with open(os.path.join(ext_dir, "package.json"), "w") as f:
    json.dump(package_json, f, indent=2)

with open(os.path.join(syntaxes_dir, "chainscript.tmLanguage.json"), "w") as f:
    json.dump(grammar_json, f, indent=2)

print(f"✅ Extension installed successfully to: {ext_dir}")
print("Please completely close and restart VS Code!")