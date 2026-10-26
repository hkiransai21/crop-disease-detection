import { AnalysisResponse } from "../types";
export type SavedCheck = {
  id: string;
  result: AnalysisResponse;
  photo?: Blob;
  variants: Record<string, AnalysisResponse>;
};
const open = () =>
  new Promise<IDBDatabase>((resolve, reject) => {
    const request = indexedDB.open("leaf-checks", 1);
    request.onupgradeneeded = () =>
      request.result.createObjectStore("checks", { keyPath: "id" });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
async function access<T>(
  mode: IDBTransactionMode,
  action: (store: IDBObjectStore) => IDBRequest<T>,
): Promise<T> {
  const db = await open();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("checks", mode);
    const request = action(tx.objectStore("checks"));
    tx.oncomplete = () => {
      db.close();
      resolve(request.result);
    };
    tx.onerror = () => {
      db.close();
      reject(tx.error);
    };
    tx.onabort = () => {
      db.close();
      reject(tx.error);
    };
  });
}
export const listChecks = () =>
  access<SavedCheck[]>("readonly", (store) => store.getAll());
export const getCheck = (id: string) =>
  access<SavedCheck | undefined>("readonly", (store) => store.get(id));
export const deleteCheck = (id: string) =>
  access("readwrite", (store) => store.delete(id));
export async function saveCheck(result: AnalysisResponse, photo?: Blob) {
  const existing = await getCheck(result.id);
  const record: SavedCheck = {
    id: result.id,
    result,
    photo: photo || existing?.photo,
    variants: { ...(existing?.result.image_sha256 === result.image_sha256 ? existing?.variants : {}), [`${result.image_sha256 || result.id}:${result.language || "en"}`]: result },
  };
  await access("readwrite", (store) => store.put(record));
  return record;
}
