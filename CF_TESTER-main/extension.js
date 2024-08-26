const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

function activate(context) {
    let disposable = vscode.commands.registerCommand('cf-tester.runCodeforcesProblem', async () => {
        const link = await vscode.window.showInputBox({ placeHolder: 'Enter Codeforces problem link' });

        if (link) {
            // Get the current file
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found.');
                return;
            }

            const filePath = editor.document.fileName;
            const directory = path.dirname(filePath);
            const outputExe = path.join(directory, 'output.exe');

            // Path to the Python scripts
            const pythonScript = path.join(context.extensionPath, 'scripts', 'parser.py');
            const checkerScript = path.join(context.extensionPath, 'scripts', 'checker.py');

            // Compile the C++ file
            exec(`g++ "${filePath}" -o "${outputExe}"`, (compileError, compileStdout, compileStderr) => {
                if (compileError) {
                    vscode.window.showErrorMessage(`Compilation Error: ${compileStderr}`);
                    return;
                }

                // Run the Python script to fetch problem
                exec(`python "${pythonScript}" 1 "${link}"`, (fetchError, fetchStdout, fetchStderr) => {
                    if (fetchError) {
                        vscode.window.showErrorMessage(`Fetch Error: ${fetchStderr}`);
                        return;
                    }

                    // Run the Python script to check the compiled executable
                    exec(`python "${checkerScript}" "${outputExe}"`, (checkError, checkStdout, checkStderr) => {
                        const panel = vscode.window.createWebviewPanel(
                            'codeforcesResults', 
                            'Codeforces Results',
                            vscode.ViewColumn.One,
                            {
                                enableScripts: true,
                            }
                        );

                        // Path to the HTML file
                        const filePath = path.join(context.extensionPath, 'media', 'results.html');
                        const fileUri = vscode.Uri.file(filePath);
                        panel.webview.html = fs.readFileSync(fileUri.fsPath, 'utf8');
                        
                        // Send results to the Webview
                        panel.webview.postMessage({
                            command: 'setResults',
                            // fetcherResults: `Fetcher Output:\n${fetchStdout}`,
                            checkerResults: `${checkStdout}`
                        });
                    });
                });
            });
        }
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
