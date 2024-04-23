import client from "@/lib/api";
import type { paths } from "@/lib/api/api";
import { useQuery } from "@tanstack/react-query";
import type { ParamsOption, RequestBodyOption } from "openapi-fetch";

type UseQueryOptions<T> = ParamsOption<T> &
  RequestBodyOption<T> & {
    // add your custom options here
    reactQuery?: {
      enabled: boolean; // Note: React Query type’s inference is difficult to apply automatically, hence manual option passing here
      // add other React Query options as needed
    };
  };

// paths
const GET_EVENTS = "/events";
const GET_EVENT_DATA = "/event/{eventId}/data";

export const getEvents = ({
  params = {},
  reactQuery,
}: UseQueryOptions<paths[typeof GET_EVENTS]["get"]> = {}) => {
  return useQuery({
    ...reactQuery,
    queryKey: [
      GET_EVENTS,
      // add any other hook dependencies here
    ],
    queryFn: async ({ signal }) => {
      const { data } = await client.GET(GET_EVENTS, {
        params,
        // body - isn’t used for GET, but needed for other request types
        signal, // allows React Query to cancel request
      });
      return data;
      // Note: Error throwing handled automatically via middleware
    },
  });
};
