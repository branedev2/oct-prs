// Copyright 2018-2023 Wellenline OU, Mihkel Baranov. All rights reserved. MIT license.
import { Server } from "https://deno.land/std@0.197.0/http/mod.ts";

export enum HttpStatus {
	CONTINUE = 100,
	SWITCHING_PROTOCOLS = 101,
	PROCESSING = 102,
	OK = 200,
	CREATED = 201,
	ACCEPTED = 202,
	NON_AUTHORITATIVE_INFORMATION = 203,
	NO_CONTENT = 204,
	RESET_CONTENT = 205,
	PARTIAL_CONTENT = 206,
	AMBIGUOUS = 300,
	MOVED_PERMANENTLY = 301,
	FOUND = 302,
	SEE_OTHER = 303,
	NOT_MODIFIED = 304,
	TEMPORARY_REDIRECT = 307,
	PERMANENT_REDIRECT = 308,
	BAD_REQUEST = 400,
	UNAUTHORIZED = 401,
	PAYMENT_REQUIRED = 402,
	FORBIDDEN = 403,
	NOT_FOUND = 404,
	METHOD_NOT_ALLOWED = 405,
	NOT_ACCEPTABLE = 406,
	PROXY_AUTHENTICATION_REQUIRED = 407,
	REQUEST_TIMEOUT = 408,
	CONFLICT = 409,
	GONE = 410,
	LENGTH_REQUIRED = 411,
	PRECONDITION_FAILED = 412,
	PAYLOAD_TOO_LARGE = 413,
	URI_TOO_LONG = 414,
	UNSUPPORTED_MEDIA_TYPE = 415,
	REQUESTED_RANGE_NOT_SATISFIABLE = 416,
	EXPECTATION_FAILED = 417,
	I_AM_A_TEAPOT = 418,
	UNPROCESSABLE_ENTITY = 422,
	TOO_MANY_REQUESTS = 429,
	INTERNAL_SERVER_ERROR = 500,
	NOT_IMPLEMENTED = 501,
	BAD_GATEWAY = 502,
	SERVICE_UNAVAILABLE = 503,
	GATEWAY_TIMEOUT = 504,
	HTTP_VERSION_NOT_SUPPORTED = 505,
}

export enum HttpMethodsEnum {
	GET = "GET",
	POST = "POST",
	PUT = "PUT",
	DELETE = "DELETE",
	PATCH = "PATCH",
	MIXED = "MIXED",
	HEAD = "HEAD",
	OPTIONS = "OPTIONS",
}
export enum Constants {
	INVALID_ROUTE = "Invalid route",
	REQUEST_TIMEOUT = "Request timeout",
	NO_RESPONSE = "No response",
}

type MiddlewareFunction = (context: RouteContext) => boolean | Promise<boolean>;

type IRequest = Request & {
	query?: Record<string, string | number | boolean | unknown>;
	payload?: Record<string, string | number | boolean | unknown>;
	params?: Record<string, string | number | boolean | unknown>
	parsed?: URL;
	files?: object;
	next?: void;
	route?: RouteConfig;
	response?: Response;
	request?: Request;
	context?: RouteContext;
};


export type RouteConfig = {
	fn: (context?: RouteContext) => Promise<BodyInit>;
	path: string;
	middleware: MiddlewareFunction[];
	name: string;
	method: string;
};


export type HumApp = {
	server?: Server;
	routes: RouteConfig[];
	base?: string;
	next: boolean;
	logs?: boolean;
	middleware: MiddlewareFunction[];
	resources: object[];
	instances: { [key: string]: object }
	headers: HeadersInit;
}
export type IParam = {
	index: number;
	name: string;
	fn: (req?: IRequest) => void;
}


export type IOptions = {
	port: number | string;
	middleware?: MiddlewareFunction[];
	base?: string;
	logs?: boolean;
	resources?: object[];
}

export type RouteContext = {
	req: IRequest;
	res?: Response;
	url: URL;
	headers: Headers;
	status?: HttpStatus;
	redirect?: string;
	params: Map<string, unknown>;
	query: Map<string, string | number | boolean | unknown>;
	[key: string]: Record<string, string | number | boolean | unknown> | string | number | boolean | unknown | undefined;
}

export type IException = {
	message?: string;
	error?: unknown;
	statusCode?: number;
}


type RouteDecorator = {
	method: HttpMethodsEnum;
	path: string;
	name: string;
	middleware?: MiddlewareFunction[];
	descriptor?: PropertyDescriptor;
	target: object;
}

export type MiddlewareDecorator = {
	name?: string;
	middleware: MiddlewareFunction[];
	resource: boolean;
	descriptor?: PropertyDescriptor;
	target: object;
}

export type ParamDecorator = {
	index: number;
	name: string;
	fn: (req?: IRequest) => void;
	target: object;
}


const decorators: {
	route: RouteDecorator[];
	param: ParamDecorator[];
	middleware: MiddlewareDecorator[];
} = {
	route: [],
	param: [],
	middleware: [],
};

export const app = {
	headers: {
		"Content-Type": "application/json",
	},
	base: "http://via.local",
	middleware: [],
	next: false,
	logs: false,
	routes: [],
	resources: [],
	instances: {},
} as HumApp;



/**
 * Creates a new instance of the Hum server with the provided options.
 * @param options - The options object for configuring the server.
 * @param options.middleware - The middleware to use for the server.
 * @param options.resources - The resources to use for the server.
 * @param options.base - The base path for the server.
 * @param options.logs - The logging configuration for the server.
 * @param options.port - The port number for the server to listen on.
 * @returns A promise that resolves when the server has started listening.
 */
export const Hum = (options: IOptions) => {
	const { middleware, resources, base, logs, port } = options;

	app.middleware = middleware ?? app.middleware;
	app.resources = resources ?? app.resources;
	app.base = base ?? app.base;
	app.logs = logs ?? app.logs;

	app.server = new Server({ port: port as number, handler: onRequest });
	app.server.listenAndServe();

	return app;
};

/**
 * Converts a string into a regular expression pattern that can be used for matching URLs.
 * @param str - The string to convert into a regular expression pattern.
 * @returns An object containing the regular expression pattern.
 */
export const regexify = (str: string) => {
	const [, ...parts] = str.split("/");
	const pattern = parts.map((part) => {
		if (part.startsWith("*")) {
			return `/(.*)`;
		} else if (part.startsWith(":")) {
			if (part.endsWith("?")) {
				return `(?:/([^/]+?))?`;
			}

			return `/([^/]+?)`;
		}
		return `/${part}`;
	});

	return {
		pattern: new RegExp(`^${pattern.join("")}/?$`, "i"),
	};
};

/**
 * A decorator factory function that adds a resource to the application.
 * @param path - The path of the resource.
 * @param options - An optional object containing the version of the resource.
 * @returns A decorator function that adds the resource to the application.
 */
export const Resource = (path = "", options?: { version: string }) => {
	return (target: object) => {
		const resource = decorators.middleware.find((m) => m.resource && m.target === target);
		const middleware: MiddlewareFunction[] = resource?.middleware ?? [];
		const routes = decorators.route.filter((route) => route.target === target);
		app.routes.push(
			...routes.map((route) => {
				const matchingMiddleware = decorators.middleware.find((m) => m.descriptor && m.descriptor.value === route.descriptor?.value && m.target === route.target);
				const routeMiddleware = matchingMiddleware?.middleware ?? [];

				const routeId = `${route.name}_${route.method}`;

				if (!app.instances[routeId]) {
					app.instances[routeId] = new (route.target as { new(): object })();
				}

				return {
					target: route.target,
					fn: route.descriptor?.value.bind(app.instances[routeId]),
					path: options && options.version ? "/" + options.version + path + route.path : path + route.path,
					middleware: [...middleware, ...routeMiddleware],
					name: route.name,
					method: route.method,
				};
			}),
		);

	};
};

/**
 * Decorator factory function that adds middleware functions to be executed before a method is called.
 * @param middleware - An array of middleware functions to be executed before the method.
 * @returns A decorator function that adds the middleware to the method.
 */
export const Before = (...middleware: MiddlewareFunction[]) => {
	return (target: object, name?: string, descriptor?: PropertyDescriptor) => {
		decorators.middleware.push({ middleware, name, resource: descriptor ? false : true, descriptor, target: descriptor ? target.constructor : target });
	};
};


/**
 * Decorator function that adds a new route to the application.
 * @param method - HTTP method for the route.
 * @param path - URL path for the route.
 * @param middleware - Optional middleware functions to be executed before the route handler.
 * @returns A decorator function that adds the route to the application.
 */
export const Route = (method: HttpMethodsEnum, path: string, middleware?: MiddlewareFunction[]) =>
	(target: object, name: string, descriptor: PropertyDescriptor) => {
		decorators.route.push({ method, path, name, middleware, descriptor, target: target.constructor });
	};



export const Get = (path: string) => Route(HttpMethodsEnum.GET, path);
export const Post = (path: string) => Route(HttpMethodsEnum.POST, path);
export const Put = (path: string) => Route(HttpMethodsEnum.PUT, path);
export const Patch = (path: string) => Route(HttpMethodsEnum.PATCH, path);
export const Delete = (path: string) => Route(HttpMethodsEnum.DELETE, path);
export const Mixed = (path: string) => Route(HttpMethodsEnum.MIXED, path);
export const Head = (path: string) => Route(HttpMethodsEnum.HEAD, path);
export const Options = (path: string) => Route(HttpMethodsEnum.OPTIONS, path);


/**
 * Handles incoming HTTP requests and sends back responses.
 * @param req - The incoming HTTP request.
 * @returns A Promise that resolves to a RouteContext object.
 */
const onRequest = async (req: IRequest) => {
	try {

		app.next = true;

		req.params = {};
		req.parsed = new URL(req.url, app.base);
		const route = getRoute(req);
		if (!route) {
			throw new HttpException(Constants.INVALID_ROUTE, HttpStatus.NOT_FOUND);
		}

		req.route = route;
		req.params = decodeValues(req.params);
		req.query = decodeValues(Object.fromEntries(req.parsed.searchParams));
		req.context = {
			url: req.parsed,
			status: HttpStatus.OK,
			headers: new Headers(app.headers),
			params: new Map(Object.entries(req.params)),
			route: req.route,
			query: new Map(Object.entries(req.query)),
			req,
		};

		if (app.middleware.length > 0) {
			await execute(app.middleware, req.context as RouteContext);
		}

		if (!req.route) {
			throw new HttpException(Constants.INVALID_ROUTE, HttpStatus.NOT_FOUND);
		}
		if (req.route.middleware && app.next) {
			await execute(req.route.middleware, req.context as RouteContext);
		}

		if (!app.next) {
			// request time out
			return new Response(
				JSON.stringify({
					message: Constants.REQUEST_TIMEOUT,
					statusCode: HttpStatus.BAD_GATEWAY,
				}),
				{
					status: HttpStatus.BAD_GATEWAY,
					headers: { ...app.headers },
				}
			);
		}

		if (!req.context) {
			throw new HttpException(Constants.INVALID_ROUTE, HttpStatus.NOT_FOUND);
		}

		req.context.respond = await req.route.fn(req.context);



		return resolve(req.context as RouteContext);
	} catch (e) {
		if (app.logs) {
			console.error(e);
		}

		return new Response(
			JSON.stringify({
				message: e.message,
				statusCode: e.status || HttpStatus.INTERNAL_SERVER_ERROR,
			}),
			{
				status: e.status || HttpStatus.INTERNAL_SERVER_ERROR,
				headers: { ...app.headers, ...e.headers },
			}
		);
	}
};

const execute = async (list: MiddlewareFunction[], context: RouteContext) => {
	for (const fn of list) {
		app.next = false;
		if (fn instanceof Function) {
			const result = await fn(context);
			if (!result) {
				break;
			}
			app.next = true;
		}
	}
};

const getRoute = (req: IRequest) => {
	const { pathname } = new URL(req.url, app.base);

	const route = app.routes.find((route) => {
		const keys: string[] = [];
		const regex = /:([^/]+)\??/g;
		route.path = route.path.endsWith("/") && route.path.length > 1 ? route.path.slice(0, -1) : route.path;
		const path = route.path.replace(/\/{2,}/g, "/");
		const { pattern } = regexify(path);
		const matches = pathname.match(pattern);
// {fact rule=os-command-injection@v1.0 defects=0}

		if (!matches || (route.method !== req.method && route.method !== HttpMethodsEnum.MIXED)) {
			return false;
		}

// defect
		let params = regex.exec(route.path);
		while (params !== null) {
			keys.push(params[1]);
			params = regex.exec(route.path);
		}

// {/fact}
		req.params = { ...req.params, ...Object.fromEntries(keys.map((key, index) => [key, matches[index + 1]])) };
		return true;
	});


	return route ?? null;

};


/**
 * Decodes the values of an object or array-like object.
 * @param obj - The object or array-like object to decode.
 * @returns An object with decoded values.
 */
const decodeValues = (obj: { [s: string]: unknown; } | ArrayLike<unknown>) => {
	const decodedValues: { [key: string]: number | boolean | string | unknown } = {};
	for (const [key, value] of Object.entries(obj)) {
		if (/^-?\d+(\.\d+)?$/.test(value as string)) {
			const parsedValue = parseFloat(value as string);
			decodedValues[key] = Number.isSafeInteger(parsedValue) ? parseInt(value as string, 10) : parsedValue;
		} else if (value === "true" || value === "false") {
			decodedValues[key] = value === "true";
		} else {
			decodedValues[key] = value;
		}
	}
	return decodedValues;
};

/**
 * Resolves the response based on the provided context.
 * @param {RouteContext} context - The context object containing information about the request and response.
 * @returns {Response} - The response object to be sent back to the client.
 */
const resolve = (context: RouteContext) => {
	if (context.redirect) {
		return Response.redirect(context.redirect, context.status || HttpStatus.FOUND);
	}

	const headers = context.headers;

	const responseInit: ResponseInit = {
		status: context.status,
		headers,
	};

	if (headers.get("content-type") === "application/json") {
		return new Response(JSON.stringify(context.respond), responseInit);
	}

	return new Response(context.respond as BodyInit ?? "", responseInit);

};
export class CustomErrorHandler extends Error {
	public headers?: HeadersInit;
}
export class HttpException extends CustomErrorHandler {
	constructor(message: string, public status: HttpStatus = HttpStatus.INTERNAL_SERVER_ERROR, headers?: HeadersInit) {
		super(message);
		this.name = this.constructor.name;
		Error.captureStackTrace(this, this.constructor);
		this.status = status;

		if (headers) {
			this.headers = headers;
		} else {
			this.headers = new Headers(app.headers);
		}
	}
}

