use std::env;
use std::fs::File;
use std::io::{self, prelude::*};
use std::path::PathBuf;
use std::process::{self, Command};
use std::collections::HashMap;

fn execute_command(command: &str) {
    Command::new("sh").args(["-c", command]).status().ok();
}

#[derive(Default)]
struct Stpl {
    symbols: HashMap<String, Vec<String>>,
    creating: Option<String>,
    depth: usize,
    init_read: bool,
    init_path: PathBuf
}

const MAX_EVAL_DEPTH: usize = 1024;

impl Stpl {
    fn new() -> Self {
        let mut stpl = Stpl::default();

        stpl.init_path = env::current_exe().unwrap();
        stpl.init_path.pop();
        stpl.init_path.push("init.conf");

        stpl.init();
        return stpl;
    }

    fn init(&mut self) {
        self.init_read = false;

        let file = File::open(&self.init_path).expect("could not open file");
        let reader = io::BufReader::new(file);

        self.eval_lines(reader.lines());
        self.init_read = true;
    }

    fn eval_line(&mut self, line: &str) -> bool {
        if self.depth > MAX_EVAL_DEPTH {
            eprintln!("Error: exceeded maximum evaluation depth");
            return false;
        }

        let line = line.trim();

        if let Some(symbol) = &self.creating {
            if line == ";;" {
                self.creating = None;
            } else {
                self.symbols.get_mut(symbol).unwrap().push(String::from(line));
            }
        } else {
            let mut words = line.split(' ');

            if line.starts_with('!') {
                execute_command(&line[1..]);
            } else if let Some(command) = words.next() {
                match command {
                    "help" => todo!(),

                    ":q" => process::exit(0),

                    ":w" => self.write(),

                    ":r" => self.init(),

                    ":e" => execute_command(&format!("{} {:?}", env::var("EDITOR").unwrap_or(String::from("vi")), self.init_path)),

                    ":d" => if let Some(command) = words.next() {
                        self.symbols.remove(command);
                    } else {
                        eprintln!("Error: insufficient arguments");
                        eprintln!("Usage: d COMMAND");
                    },

                    ":cd" => if let Some(path) = words.next() {
                        env::set_current_dir(path).ok();
                    } else {
                        eprintln!("Error: insufficient arguments");
                        eprintln!("Usage: cd PATH");
                    }

                    ":c" => if let Some(command) = words.next() {
                        self.symbols.insert(String::from(command), vec![]);
                        self.creating = Some(String::from(command));
                    } else {
                        eprintln!("Error: insufficient arguments");
                        eprintln!("Usage: c COMMAND");
                    }

                    command => if let Some(lines) = self.symbols.get(command) {
                        self.depth += 1;
                        for line in lines.clone() {
                            if !self.eval_line(&line) {
                                self.depth -= 1;
                                return false;
                            }
                        }
                        self.depth -= 1;
                    } else {
                        eprintln!("Error: command `{}` is not defined", command);
                    }
                }
            }
        }

        return true;
    }

    fn eval_lines<B: io::BufRead>(&mut self, lines: io::Lines<B>) {
        self.depth = 0;
        self.print_prompt();

        for line in lines {
            self.eval_line(&line.unwrap());
            self.print_prompt();
        }
    }

    fn print_prompt(&self) {
        if self.init_read {
            match &self.creating {
                Some(_) => print!("| "),
                None => print!("> ")
            }

            io::stdout().flush().expect("could not flush stdout");
        }
    }

    fn write(&self) {
        let mut file = File::create(&self.init_path).expect("could not open file");

        for (symbol, value) in &self.symbols {
            writeln!(file, ":c {}\n{}\n;;", symbol, value.join("\n")).expect("could not write to file");
        }
    }
}

fn main() {
    let mut stpl = Stpl::new();
    stpl.eval_lines(io::stdin().lock().lines());
}
