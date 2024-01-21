use downloader::{Download, Downloader, progress::Reporter};
use std::sync::{Arc, Mutex};
use std::time::Instant;

struct ProgressReporter {
    total_size: Mutex<Option<u64>>,
    start_time: Instant,
    last_reported_time: Mutex<Instant>,
}

impl ProgressReporter {
    fn new() -> Self {
        let now = Instant::now();
        Self {
            total_size: Mutex::new(None),
            start_time: now,
            last_reported_time: Mutex::new(now),
        }
    }
}

impl Reporter for ProgressReporter {
    fn setup(&self, max_progress: Option<u64>, _message: &str) {
        
        let mut total_size = self.total_size.lock().unwrap();
        *total_size = max_progress;
    }

    fn progress(&self, progress: u64) {
        let now = Instant::now();
        let mut last_reported_time = self.last_reported_time.lock().unwrap();
        if now.duration_since(*last_reported_time).as_secs() >= 1 {
            if let Some(total_size) = *self.total_size.lock().unwrap() {
                println!("Загружено {} из {} байт", progress, total_size);
            } else {
                println!("Загружено {} байт", progress);
            }
            *last_reported_time = now;
        }
    }

    fn set_message(&self, _message: &str) {
       
    }

    fn done(&self) {
        
        println!("Загрузка файла завершена!");
    }
}

fn main() {

    // let terminalUrl: String = std::env::args().nth(1).expect("Не передан URL файла");

    let downloads = vec![
        Download::new("https://drive.google.com/uc?export=download&id=1pmU0hNa6oQZuyPBC39tUKtJkHX7epYOX")
            .progress(Arc::new(ProgressReporter::new())),
    ];

    let mut downloader = Downloader::builder()
        .build()
        .unwrap();

    match downloader.download(&downloads) {
        Ok(_) => println!("Файл успешно загружен!"),
        Err(e) => println!("Произошла ошибка при загрузке файла: {:?}", e),
    }
}
