export declare global {
  interface Window {
    getCookie: (name: string) => string | undefined;
  }
}
