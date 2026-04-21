export type ChatRequest = {
  requesterId: string;
  message: string;
};

export type ChatReply = {
  requestId: string;
  answer: string;
  containsCompensation: boolean;
};

