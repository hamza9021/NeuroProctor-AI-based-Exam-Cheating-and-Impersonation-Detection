const Card = ({
  children,
  className = '',
  padding = 'lg',
  ...props
}) => {
  const paddings = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  return (
    <div
      className={`bg-white rounded-xl shadow-sm border border-neutral-200 ${paddings[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
