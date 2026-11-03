/* Chạy backend Python ngay trong trình duyệt bằng Pyodide, dùng cho bản đăng trên GitHub Pages.
   Các request /api được chuyển cho Flask test client nên logic lá số giữ nguyên như bản chạy server. */

(() => {
    const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
    const BUILTIN_PACKAGES = ['micropip', 'python-dateutil', 'pillow'];
    const PYPI_PACKAGES = ['flask==3.0.0', 'flask-cors==4.0.0', 'python-dotenv==1.0.0', 'reportlab==4.0.9'];
    const APP_DIR = '/app';
    // pdf_report.py tìm font DejaVu ở đường dẫn này khi chạy trên Linux.
    const FONT_DIR = '/usr/share/fonts/truetype/dejavu';

    const BOOT_SCRIPT = `
import sys
sys.path.insert(0, "${APP_DIR}")
import app as tuvi


class SerialExecutor:
    """Pyodide không tạo được luồng nên chạy tuần tự thay cho ThreadPoolExecutor."""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def map(self, fn, *iterables):
        return map(fn, *iterables)


tuvi.ThreadPoolExecutor = SerialExecutor
client = tuvi.app.test_client()


def handle(method, path, body):
    response = client.open("/api" + path, method=method, data=body,
                           content_type="application/json" if body else None)
    return response.status_code, response.content_type, response.get_data()
`;

    function loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Không tải được ${src}`));
            document.head.append(script);
        });
    }

    async function fetchOk(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Không tải được ${url}`);
        }
        return response;
    }

    async function boot() {
        await loadScript(`${PYODIDE_URL}pyodide.js`);
        const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
        await pyodide.loadPackage(BUILTIN_PACKAGES);
        await pyodide.pyimport('micropip').install(PYPI_PACKAGES);

        const manifest = await (await fetchOk('py/manifest.json')).json();
        pyodide.FS.mkdirTree(APP_DIR);
        await Promise.all(manifest.modules.map(async (name) => {
            pyodide.FS.writeFile(`${APP_DIR}/${name}`, await (await fetchOk(`py/${name}`)).text());
        }));
        pyodide.FS.mkdirTree(FONT_DIR);
        await Promise.all(manifest.fonts.map(async (name) => {
            const data = new Uint8Array(await (await fetchOk(`fonts/${name}`)).arrayBuffer());
            pyodide.FS.writeFile(`${FONT_DIR}/${name}`, data);
        }));

        pyodide.runPython(BOOT_SCRIPT);
        return pyodide.globals.get('handle');
    }

    let handlePromise = null;

    /** Khởi động Pyodide một lần cho mỗi trang; lần đầu mất vài giây để tải. */
    function ready() {
        handlePromise ??= boot();
        return handlePromise;
    }

    /** Giống fetch() nhưng xử lý request /api bằng Flask chạy trong trình duyệt. */
    async function pythonFetch(path, options = {}) {
        const handle = await ready();
        const result = handle(options.method || 'GET', path, options.body ?? null);
        try {
            const [status, contentType, data] = result.toJs();
            return new Response(data, { status, headers: { 'Content-Type': contentType } });
        } finally {
            result.destroy();
        }
    }

    window.tuviPython = { ready, fetch: pythonFetch };
    ready().catch(() => {});
})();
